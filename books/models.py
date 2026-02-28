from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count


# Create your models here.
class Category(models.Model):
    category_name   = models.CharField(max_length=100, unique=True)
    slug            = models.SlugField(max_length=100, unique=True)
    description     = models.TextField(blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name

class Book(models.Model):
    category            = models.ForeignKey(Category,on_delete=models.CASCADE, related_name='books')
    cover_image         = models.ImageField(upload_to='books/cover_image/', blank=True, null=True)
    title               = models.CharField(max_length=225, unique=True)
    slug                = models.SlugField(max_length=225, unique=True)
    isbn                = models.CharField(max_length=30, unique=True)
    description         = models.TextField(blank=True)
    author              = models.CharField(max_length=100)
    price               = models.DecimalField(max_digits=10, decimal_places=2)
    publication_date    = models.DateField(null=True, blank=True)
    stock               = models.IntegerField()
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title','category','author'],
                name='unique_book_per_category_author'
            )
        ]

    @property
    def average_rating(self):
        avg = self.reviews.filter(status=True).aggregate(Avg("rating"))["rating__avg"]
        return round(avg, 2) if avg else 0

    @property
    def count_review(self):
        count = self.reviews.filter(status=True).aggregate(Count("rating"))["rating__count"]
        return count or 0

    def __str__(self):
        return self.title

class ReviewRating(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    book        = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    subject     = models.CharField(max_length=100)
    review      = models.TextField()
    rating      = models.FloatField()
    status      = models.BooleanField(default=True)
    ip          = models.CharField(max_length=100, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "book")

    def __str__(self):
        return f"{self.subject} - {self.rating}"