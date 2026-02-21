from django.urls import path
from .views import CartView, AddToCartView

urlpatterns = [
    path('', view=CartView.as_view(), name='cart'),
    path('add/', view=AddToCartView.as_view(), name='add-to-cart'),
]