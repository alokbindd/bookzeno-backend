from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils.crypto import get_random_string
from rest_framework import generics, status
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from books.models import Book
from carts.models import Cart
from core.utils import error_response, success_response
from orders.models import Order, OrderProduct, Payment
from orders.pagination import OrderCursorPagination
from orders.serializers import (CheckoutSerializer, OrderDetailserializer,
                                OrderHistorySerializer)
from orders.services import capture_paypal_order, create_paypal_order

# Create your views here.

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    TAX_RATE = Decimal("0.18")

    def post(self,request):
        current_user = request.user
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        #Get cart
        try:
            cart = Cart.objects.get(user=current_user)
        except Cart.DoesNotExist:
            return error_response(message="Cart is empty", status=status.HTTP_400_BAD_REQUEST)

        # check cart_item
        cart_items = cart.items.all()
        if not cart_items.exists():
            return error_response(message="Cart is empty", status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            subtotal = Decimal("0.00")
            validated_items = []

            # Lock rows + validate stock + fetch fresh price
            for item in cart_items:
                book = Book.objects.select_for_update().get(id=item.book_id)

                if book.stock < item.quantity:
                    return error_response(
                        message=f"{book.title} has insufficient stock",
                        errors={"available": book.stock, "requested": item.quantity}, 
                        status=status.HTTP_409_CONFLICT
                        )

                line_total = book.price * item.quantity
                subtotal += line_total

                validated_items.append({
                    "book": book,
                    "quantity": item.quantity,
                    "price": book.price
                })
            
            tax = (subtotal * self.TAX_RATE).quantize(Decimal("0.01"))
            grand_total = subtotal + tax

            while True:
                current_date = date.today().strftime("%Y%m%d")
                random_number = get_random_string(6).upper()
                order_number = f"{current_date}-{random_number}"
                
                if not Order.objects.filter(order_number=order_number).exists():
                    break

            # Create Order (pending)
            order = Order.objects.create(
                user=current_user,
                order_number=order_number,
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                phone_number=data["phone_number"],
                address_line_1=data["address_line_1"],
                address_line_2=data.get("address_line_2", ""),
                state=data["state"],
                city=data["city"],
                pincode=data["pincode"],
                country=data["country"],
                order_note=data.get("order_note",""),
                order_total=subtotal,
                tax=tax,
                grand_total=grand_total,
                status="pending",
                is_ordered=False
            )

            # create OrderProduct rows
            for item in validated_items:
                OrderProduct.objects.create(
                    order=order,
                    book=item["book"],
                    quantity=item["quantity"],
                    book_price=item["price"],
                    ordered=False
                )

            return success_response(
                message="Order created successfully",
                data={
                    "order_id":order.id,
                    "order_number":order.order_number,
                    "subtotal":subtotal,
                    "tax":tax,
                    "grand_total":grand_total
                },
                status=status.HTTP_201_CREATED)
            
class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return error_response(message="Order not found",status=status.HTTP_404_NOT_FOUND)
        
        #security checks
        if order.user != request.user:
            return error_response(message="Unauthorized", status=status.HTTP_403_FORBIDDEN)
        
        if order.status != "pending":
            return error_response(message="Order cannot be Paid", status=status.HTTP_409_CONFLICT)
        
        paypal_response = create_paypal_order(order)

        if "id" not in paypal_response:
            return error_response(message="Paypal error",errors=paypal_response, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        order.provider_order_id = paypal_response["id"]
        order.save(update_fields=["provider_order_id"])

        # Extract approval URL
        approval_url = None
        for link in paypal_response.get("links", []):
            if link["rel"] == "approve":
                approval_url = link["href"]
                break

        return success_response(
            message="Payment created",
            data={"paypal_order_id": paypal_response["id"],"approval_url": approval_url},
            status=status.HTTP_201_CREATED
        )
    
class CapturePayementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        paypal_order_id = request.data.get("paypal_order_id")

        if not paypal_order_id:
            return error_response(message="Paypal order id is required", status=status.HTTP_400_BAD_REQUEST)

        # Capture payment from PayPal
        paypal_response = capture_paypal_order(paypal_order_id)

        if paypal_response.get("status") != "COMPLETED":
            return error_response(
                message="Payment not completed",
                errors={"details": paypal_response},
                status=status.HTTP_409_CONFLICT
            )

        # Extract data from response
        purchase_units  = paypal_response["purchase_units"][0]
        
        if not purchase_units.get("payments"):
            return error_response(message="Invalid payment response", status=status.HTTP_400_BAD_REQUEST)
        
        captures = purchase_units["payments"].get("captures")

        if not captures:
            return error_response(message="No capture found", status=status.HTTP_400_BAD_REQUEST)

        payment         = captures[0]
        transaction_id  = payment["id"]
        captured_amount = payment["amount"]["value"]
        currency_code   = payment["amount"]["currency_code"]
        
        if currency_code != "USD":
            return error_response(message="Currency mismatch", status=status.HTTP_400_BAD_REQUEST)
        
        # Critical transaction block
        with transaction.atomic():
            if Payment.objects.select_for_update().filter(payment_id=transaction_id).exists():
                return success_response(
                    message="Payment already processed"
                )
            
            # Fetch order using provider_order_id
            try:
                order = Order.objects.select_for_update().get(provider_order_id=paypal_order_id)
            except Order.DoesNotExist:
                return error_response(message="No Order with this reference id", status=status.HTTP_404_NOT_FOUND)
            
            if order.user != request.user:
                return error_response(message="Unauthorized", status=status.HTTP_403_FORBIDDEN)
            
            if order.status == "paid":
                return success_response(message="Order already has been processed")
            
            captured_amount = Decimal(captured_amount)
            expected_total = (order.order_total + order.tax).quantize(Decimal("0.01"))

            if captured_amount != expected_total:
                return error_response(
                    message="Amount mismatch",
                    errors={"expected": expected_total,"recieved": captured_amount,},
                    status=status.HTTP_409_CONFLICT
                )
                    
            # Deduct stock safely
            for item in order.items.all():
                book = Book.objects.select_for_update().get(id=item.book_id)

                if book.stock < item.quantity:
                    raise ValidationError(f"{book.title} out of stock")

                Book.objects.filter(id=book.id).update(
                    stock=F("stock") - item.quantity
                )

                OrderProduct.objects.filter(order=order,book=book).update(
                    ordered=True
                )

            # Create payment record
            Payment.objects.create(
                user=order.user,
                order=order,
                payment_id=transaction_id,
                payment_method="PayPal",
                amount_paid=expected_total,
                status="completed",
            )

            #update order
            order.status = "paid"
            order.is_ordered = True
            order.save()

            # Clear cart items
            cart = Cart.objects.filter(user=order.user).first()
            
            if cart:
                cart.items.all().delete()
        
        return success_response(
            message="Payment successful",
            data={"order_id": order.id}
        )

class OrderHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderHistorySerializer
    pagination_class = OrderCursorPagination
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at').select_related("user")

class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailserializer
    lookup_field = 'order_number'
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("payments","items__book")