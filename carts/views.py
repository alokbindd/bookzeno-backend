from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .models import Cart,CartItem
from .serializers import CartItemSerializer
from rest_framework.response import Response
from rest_framework import status
from books.models import Book
from .services import merge_carts, get_or_create_cart, get_cart

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
        return Response(serializer.data)

class MergeCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        session_key = request.session.session_key

        if not session_key:
            return Response(
                {"message":"No guest session"},
                status=status.HTTP_200_OK
            )
        
        merged = merge_carts(user=request.user,session_key=session_key)

        if merged:
            return Response({"message":"Cart merged successfully"})
        else:
            return Response({"message":"No guest cart to merge"})


class AddToCartView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity',1))
        if not book_id:
            return Response({"error": "Book ID required"}, status=400)
        
        book = get_object_or_404(Book,id=book_id)

        if quantity <= 0:
            return Response({"error":"Invalid quantity"}, status=400)
        
        if quantity > book.stock:
            return Response({"error":"Not enough stock"}, status=400)

        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book=book
        )

        if created:
            cart_item.quantity = quantity
        else:
            if cart_item.quantity + quantity > book.stock:
                return Response({"error":"Stock limit exceeded"},status=400)
            cart_item.quantity += quantity
        
        cart_item.save()

        return Response({'message':'Book Added to cart'})

class RemoveCartItemView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        cart = get_cart(request)

        if not cart:
            return Response({"error": "Cart not found"}, status=404)

        cart_item = get_object_or_404(
            CartItem,
            cart=cart,
            book=book
        )
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            return Response({'message':'Reduced quantity by 1'})
        else:
            cart_item.delete()
            return Response({'message':'Item removed from cart'})

class DeleteCartItemView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        cart = get_cart(request)

        if not cart:
            return Response({"error": "Cart not found"}, status=404)
        
        cart_item = get_object_or_404(
            CartItem,
            book=book,
            cart=cart
        )
        cart_item.delete()
        return Response({"message":"Item removed from cart"})
    
