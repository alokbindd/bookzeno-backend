from django.contrib import admin
from .models import Category, Book

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name','slug')

class BookAdmin(admin.ModelAdmin):
    list_display = ('category','title','slug','isbn','author','price','publication_date','stock')
    ordering = ('-publication_date',)


# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Book, BookAdmin)