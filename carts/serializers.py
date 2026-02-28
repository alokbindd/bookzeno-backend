from rest_framework import serializers

from books.models import Book

from carts.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    book_price = serializers.ReadOnlyField(source='book.price')

    class Meta:
        model = CartItem
        fields = ['id','book','book_title','book_price','quantity']

