from django.contrib import admin

from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    readonly_fields = ['book','quantity']
    extra = 0

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

# Register your models here.
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)