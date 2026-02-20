from django.db import models
from django.contrib.auth.models import User
from books.models import Book
# Create your models here.

class Payment(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)  
    payment_id      = models.CharField(max_length=225,unique=True)
    payment_method  = models.CharField(max_length=100)
    amount_paid     = models.DecimalField(max_digits=10,decimal_places=2)
    status          = models.CharField(max_length=100)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id
    
class Order(models.Model):
    STATUS_CHOICE = (
        ('pending','Pending'),
        ('paid','Paid'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled'),
    )

    order_number    = models.CharField(max_length=225, unique=True)
    user            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment         = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    email           = models.EmailField()
    phone_number    = models.CharField(max_length=15)
    address_line_1  = models.CharField(max_length=50)
    address_line_2  = models.CharField(max_length=50, blank=True)
    state           = models.CharField(max_length=20)
    city            = models.CharField(max_length=20)
    pincode         = models.CharField(max_length=20)
    country         = models.CharField(max_length=20)
    order_note      = models.TextField(blank=True)
    order_total     = models.DecimalField(max_digits=10, decimal_places=2)
    tax             = models.DecimalField(max_digits=10, decimal_places=2)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')
    is_ordered      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - #{self.order_number}'

class OrderProduct(models.Model):
    order       = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book        = models.ForeignKey(Book, on_delete=models.PROTECT)
    quantity    = models.PositiveIntegerField()
    book_price  = models.DecimalField(max_digits=10, decimal_places=2)
    ordered     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.book.title