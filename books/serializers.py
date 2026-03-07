from rest_framework import serializers

from books.models import Book, Category, ReviewRating


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','category_name','slug']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    rating = serializers.FloatField(min_value=1, max_value=5)
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = ReviewRating
        fields = [
            "id",
            "user",
            "reviewer_name",
            "subject",
            "review",
            "rating",
            "created_at",
        ]

    def get_reviewer_name(self,obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    reviews = ReviewSerializer(read_only=True, many=True)

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
            'reviews',
            'average_rating',
            'count_review',
        ]

