from django.urls import path

from .views import (CapturePayementView, CheckoutView, CreatePaymentView,
                    OrderDetailView, OrderHistoryView)

urlpatterns =[
    path('orders/', view=OrderHistoryView.as_view(), name='order-history'),
    path('orders/checkout/', view=CheckoutView.as_view(), name='checkout'),
    path('orders/<str:order_number>/payment/create/', view=CreatePaymentView.as_view(), name='create-payment'),
    path('orders/payment/capture/', view=CapturePayementView.as_view(), name='capture-payment'),
    path('orders/<str:order_number>/',view=OrderDetailView.as_view(),name='order-detail'),
]