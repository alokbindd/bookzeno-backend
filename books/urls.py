from django.urls import path
from .views import BookView,BookDetailView

urlpatterns = [
    path('',view=BookView.as_view(),name='book-list'),
    path('<slug:slug>/',view=BookDetailView.as_view(),name='book-detail')
]