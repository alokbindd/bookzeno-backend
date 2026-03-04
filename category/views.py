from django.shortcuts import render
from books.models import Category
from books.serializers import CategorySerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny

# Create your views here.

class CatergoryView(generics.ListAPIView):
    queryset = Category.objects.all().order_by("category_name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
