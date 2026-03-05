from django.contrib import admin

from books.models import Book, Category, ReviewRating


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name','slug')

class BookAdmin(admin.ModelAdmin):
    list_display = ('id','category','title','slug','isbn','author','price','publication_date','stock')
    ordering = ('-publication_date',)

class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('id','user','book','subject','rating','status')
    list_editable = ('status',)
    ordering = ('id',)

# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)