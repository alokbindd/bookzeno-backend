from django.db import models
from django.contrib.auth.models import User
from books.models import Book

# Create your models here.
class Cart(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id  = models.CharField(max_length=225, null=True, blank=True, unique=True)
    date_added  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f'Cart - {self.user.username}'
        return f'Cart - {self.session_id}'
    
class CartItem(models.Model):
    cart        = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book        = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity    = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart','book'],
                name='unique_book_cart'
            )
        ]
        
    def __str__(self):
        return f'{self.book.title} ({self.quantity})'