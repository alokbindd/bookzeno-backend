from django.contrib import admin

from .models import Order, OrderProduct, Payment

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ['book','quantity','book_price','ordered']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','user','full_name','phone_number','email','city','order_total','tax','grand_total','status','is_ordered','created_at']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name','email']
    list_per_page = 20
    inlines = [OrderProductInline]

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order','book','quantity','book_price','ordered']
    list_per_page = 10

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "order", "amount_paid", "status", "created_at")
    list_filter = ("status",)
