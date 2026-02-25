from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from decimal import Decimal

from books.models import Book
from carts.models import Cart
from orders.models import Order, OrderProduct, Payment

from orders.services import create_paypal_order, capture_paypal_order

from orders.serializers import CheckoutSerializer
from django.utils.crypto import get_random_string
from django.db import transaction
from django.db.models import F

from datetime import date

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
            return Response({"error":"Cart is empty"}, status=400)

        # check cart_item
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response({"error":"Cart is empty"}, status=400)
        
        with transaction.atomic():
            subtotal = Decimal("0.00")
            validated_items = []

            # Lock rows + validate stock + fetch fresh price
            for item in cart_items:
                book = Book.objects.select_for_update().get(id=item.book_id)

                if book.stock < item.quantity:
                    return Response({
                        "error": f"{book.title} has insufficient stock",
                        "available": book.stock,
                        "requested": item.quantity
                    }, status=400)

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

            return Response({
                "message":"Order created successfully",
                "order_id":order.id,
                "order_number":order.order_number,
                "subtotal":subtotal,
                "tax":tax,
               "grand_total":grand_total
            },status=201)
            
class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error":"Order not found"},status=404)
        
        #security checks
        if order.user != request.user:
            return Response({"error":"Unauthorized"},status=403)
        
        if order.status != "pending":
            return Response({"error":"Order cannot be Paid"},status=403)
        
        paypal_response = create_paypal_order(order)

        if "id" not in paypal_response:
            return Response({"error":"Paypal error","details": paypal_response},status=400)

        order.provider_order_id = paypal_response["id"]
        order.save(update_fields=["provider_order_id"])

        # Extract approval URL
        approval_url = None
        for link in paypal_response.get("links", []):
            if link["rel"] == "approve":
                approval_url = link["href"]
                break

        return Response({
            "paypal_order_id": paypal_response["id"],
            "approval_url": approval_url
        })
    
class CapturePayementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        paypal_order_id = request.data.get("paypal_order_id")

        if not paypal_order_id:
            return Response({"error":"Paypal order id is required"},status=400)

        # Capture payment from PayPal
        paypal_response = capture_paypal_order(paypal_order_id)

        if paypal_response.get("status") != "COMPLETED":
            return Response({
                "message":"Payment not completed",
                "details": paypal_response,
            },status=400)

        # Extract data from response
        purchase_units  = paypal_response["purchase_units"][0]
        
        if not purchase_units.get("payments"):
            return Response({"error": "Invalid payment response"}, status=400)
        
        captures = purchase_units["payments"].get("captures")

        if not captures:
            return Response({"error": "No capture found"}, status=400)

        payment         = captures[0]
        transaction_id  = payment["id"]
        captured_amount = payment["amount"]["value"]
        currency_code   = payment["amount"]["currency_code"]
        
        if currency_code != "USD":
            return Response({"error": "Currency mismatch"}, status=400)
        
        # Critical transaction block
        with transaction.atomic():
            if Payment.objects.select_for_update().filter(payment_id=transaction_id).exists():
                return Response({
                    "message":"Payment already processed"
                },status=200)
            
            # Fetch order using provider_order_id
            try:
                order = Order.objects.select_for_update().get(provider_order_id=paypal_order_id)
            except Order.DoesNotExist:
                return Response({"error":"No Order with this reference id"},status=404)
            
            if order.user != request.user:
                return Response({"error":"Unauthorized"},status=403)
            
            if order.status == "paid":
                return Response({"message":"Order already has been processed"},status=200)
            
            captured_amount = Decimal(captured_amount)
            expected_total = (order.order_total + order.tax).quantize(Decimal("0.01"))

            if captured_amount != expected_total:
                return Response({
                    "error":"Amount mismatch",
                    "expected": expected_total,
                    "recieved": captured_amount,
                },status=400)
                    
            # Deduct stock safely
            for item in order.items.all():
                book = Book.objects.select_for_update().get(id=item.book_id)

                if book.stock < item.quantity:
                    raise ValidationError(f"{book.title} out of stock")

                Book.objects.filter(id=book.id).update(
                    stock=F("stock") - item.quantity
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
        
        return Response({
            "message":"Payment successful",
            "order_id": order.id
        }, status=200)
