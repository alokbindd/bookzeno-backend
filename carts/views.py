from django.db.models import F
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from books.models import Book
from carts.models import Cart, CartItem
from carts.serializers import CartItemSerializer
from carts.services import get_cart, get_or_create_cart, merge_carts
from core.utils import error_response, success_response


# Create your views here.
def get_session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

class CartView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request): 
        if request.user.is_authenticated:
            cart , _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = get_session_id(request)
            cart , _ = Cart.objects.get_or_create(session_id=session_key)
        
        items = cart.items.all()
        serializer = CartItemSerializer(items, many=True)
        return success_response(data=serializer.data)

class MergeCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        session_key = request.session.session_key

        if not session_key:
            return success_response(message="No guest session")
        
        merged = merge_carts(user=request.user,session_key=session_key)

        if merged:
            return success_response(message="Cart merged successfully")
        else:
            return success_response(message="No guest cart to merge")


class AddToCartView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity',1))
        if not book_id:
            return error_response(message="Book ID required")
        
        book = get_object_or_404(Book,id=book_id)

        if quantity <= 0:
            return error_response(message="Invalid quantity", status=status.HTTP_400_BAD_REQUEST)
        
        if quantity > book.stock:
            return error_response(message="Not enough stock", status=status.HTTP_409_CONFLICT)

        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book=book
        )

        if created:
            cart_item.quantity = quantity
        else:
            if cart_item.quantity + quantity > book.stock:
                return error_response(message="Stock limit exceeded", status=status.HTTP_409_CONFLICT)
            cart_item.quantity += quantity
        
        cart_item.save()

        return success_response(message="Book Added to cart")

class RemoveCartItemView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        cart = get_cart(request)

        if not cart:
            return success_response(message="Cart not found")

        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            book=book
        )
        if cart_item.quantity > 1:
            CartItem.objects.filter(id=cart_item.id).update(
                quantity=F("quantity") - 1
            )
            return success_response(message="Reduced quantity by 1")
        else:
            cart_item.delete()
            return success_response(message="Item removed from cart", status=status.HTTP_204_NO_CONTENT)

class DeleteCartItemView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        cart = get_cart(request)

        if not cart:
            return success_response(message="Cart not found")
        
        cart_item = get_object_or_404(
            CartItem,
            book=book,
            cart=cart
        )
        cart_item.delete()
        return success_response(message="Item removed from cart", status=status.HTTP_204_NO_CONTENT)
    
