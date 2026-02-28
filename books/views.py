from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from books.serializers import BookSerializer, ReviewSerializer
from books.models import Book, ReviewRating
from core.utils import success_response , error_response
from orders.models import OrderProduct
# Create your views here.

class BookView(generics.ListAPIView):
    queryset = Book.objects.all().order_by("created_at")
    serializer_class = BookSerializer
    permission_classes = [AllowAny]

class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class AdminBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'

class SubmitReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        book = get_object_or_404(Book, slug=slug)

        has_purchased = OrderProduct.objects.filter(
            order__user=request.user,
            order__status="paid",
            book=book
        ).exists()

        print(has_purchased)

        if not has_purchased:
            raise PermissionDenied("You can only review books you have purchased.")

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        review, created =  ReviewRating.objects.update_or_create(
            user=request.user, 
            book=book,
            defaults={
                "subject": request.data.get("subject"),
                "review": request.data.get("review"),
                "rating": request.data.get("rating"),
                "ip": request.META.get("REMOTE_ADDR"),
                "status": True,
            }
        )

        serializer = ReviewSerializer(review)
        return success_response(data=serializer.data, status=status.HTTP_201_CREATED)
    
class BookReviewListView(APIView):
    
    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        review = ReviewRating.objects.filter(book=book).order_by("-created_at")
        serilaizer = ReviewSerializer(review, many=True)
        return success_response(data=serilaizer.data)

class DeleteReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        review = get_object_or_404(ReviewRating, book=book, user=request.user)
        review.delete()
        return success_response(message="Review Deleted")
