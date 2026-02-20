from .models import Category, Book
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','category_name','slug']

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'category',
            'title',
            'slug',
            'isbn',
            'description',
            'author',
            'price',
            'stock',
            'cover_image',
            'publication_date',
        ]

