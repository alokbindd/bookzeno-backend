from django.urls import path

from .views import (AdminBookDetailView, BookDetailView, BookReviewListView,
                    BookView, DeleteReviewView, SubmitReviewView, BookSearchView)

urlpatterns = [
    # Public
    path('books/',view=BookView.as_view(),name='book-list'),
    path("books/search/", BookSearchView.as_view(), name="book-search"),
    path('books/<slug:slug>/',view=BookDetailView.as_view(),name='book-detail'),
    path("books/<slug:slug>/review/", SubmitReviewView.as_view()),
    path("books/<slug:slug>/reviews/", BookReviewListView.as_view()),
    path("books/<slug:slug>/review/delete/", DeleteReviewView.as_view()),

    # Admin
    path('admin/books/<slug:slug>/',view=AdminBookDetailView.as_view(),name='admin-book-detail'),
]