from django.shortcuts import render
from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Cart,CartItem
from .serializers import CartItemSerializer
from rest_framework.response import Response
from rest_framework import status
from books.models import Book

# Create your views here.

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        serializers = CartItemSerializer(items, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity',1))

        book = Book.objects.get(id=book_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book=book
        )

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        
        cart_item.save()

        return Response({'message':'Book Added to cart'})