from django.db import models

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
    category    = models.ForeignKey(Category,on_delete=models.CASCADE, related_name='books')
    cover_image = models.ImageField(upload_to='books/cover_image/', blank=True, null=True)
    title       = models.CharField(max_length=225, unique=True)
    slug        = models.SlugField(max_length=225, unique=True)
    isbn        = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    author      = models.CharField(max_length=100)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.IntegerField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title