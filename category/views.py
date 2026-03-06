from django.shortcuts import get_list_or_404, get_object_or_404, render
from rest_framework import generics
from rest_framework.decorators import APIView
from rest_framework.permissions import AllowAny

from books.models import Book, Category
from books.serializers import BookSerializer, CategorySerializer
from core.utils import error_response, success_response

# Create your views here.

class CatergoryView(generics.ListAPIView):
    queryset = Category.objects.all().order_by("category_name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class CatergoryDetailView(APIView):
    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        book = get_list_or_404(Book, category=category)
        serializer = BookSerializer(book, many=True)
        return success_response(data=serializer.data)