from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import APIView
from rest_framework.response import Response
from decimal import Decimal

from books.models import Book
from carts.models import Cart
from orders.models import Order, OrderProduct

from orders.serializers import CheckoutSerializer
from django.utils.crypto import get_random_string
from django.db import transaction
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

            current_date = date.today().strftime("%Y%m%d")
            random_number = get_random_string(6).upper()
            order_number = f"{current_date}-{random_number}"

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
            
    