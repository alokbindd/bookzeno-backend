from django.urls import path
from .views import CartView, AddToCartView, RemoveCartItemView, MergeCartView, DeleteCartItemView

urlpatterns = [
    path('', view=CartView.as_view(), name='cart'),
    path('add/', view=AddToCartView.as_view(), name='add-to-cart'),
    path('merge/', view=MergeCartView.as_view(), name='merge-cart'),
    path('item/<int:book_id>/', DeleteCartItemView.as_view(), name='delete-cart-item'),
    path('item/<int:book_id>/decrement/', RemoveCartItemView.as_view(), name='remove-cart-item'),
]