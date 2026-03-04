from django.urls import path

from category.views import CatergoryView

urlpatterns = [
    path("category/", CatergoryView.as_view(), name='category-list'),
]