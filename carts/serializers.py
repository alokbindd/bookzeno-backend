from rest_framework import serializers

from books.models import Book
from carts.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    book_price = serializers.ReadOnlyField(source='book.price')
    book_image = serializers.ImageField(source='book.cover_image', read_only=True)
    book_slug = serializers.CharField(source='book.slug', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id','book','book_title','book_image','book_slug','book_price','quantity']

