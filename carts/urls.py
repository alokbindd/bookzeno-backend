from django.urls import path
from .views import CartView, AddToCartView, RemoveCartItem, MergeCartView

urlpatterns = [
    path('', view=CartView.as_view(), name='cart'),
    path('add/', view=AddToCartView.as_view(), name='add-to-cart'),
    path('remove/', view=RemoveCartItem.as_view(), name='remove-cart-item'),
    path('merge/', view=MergeCartView.as_view(), name='merge-cart'),
]