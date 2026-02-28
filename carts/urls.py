from django.urls import path

from carts.views import (AddToCartView, CartView, DeleteCartItemView, MergeCartView,
                    RemoveCartItemView)

urlpatterns = [
    path('carts/', view=CartView.as_view(), name='cart'),
    path('carts/add/', view=AddToCartView.as_view(), name='add-to-cart'),
    path('carts/merge/', view=MergeCartView.as_view(), name='merge-cart'),
    path('carts/item/<int:book_id>/', DeleteCartItemView.as_view(), name='delete-cart-item'),
    path('carts/item/<int:book_id>/decrement/', RemoveCartItemView.as_view(), name='remove-cart-item'),
]