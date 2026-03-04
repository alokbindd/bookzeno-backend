from django.urls import path

from category.views import CatergoryView, CatergoryDetailView

urlpatterns = [
    path("category/", CatergoryView.as_view(), name='category-list'),
    path("category/<slug:slug>/", CatergoryDetailView.as_view(), name='category-books'),
]