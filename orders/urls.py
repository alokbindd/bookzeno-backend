from django.urls import path
from .views import CheckoutView, CreatePaymentView, CapturePayementView, OrderHistoryView, OrderDetailView

urlpatterns =[
    path('orders/', view=OrderHistoryView.as_view(), name='order-history'),
    path('orders/checkout/', view=CheckoutView.as_view(), name='checkout'),
    path('orders/capture-payment/', view=CapturePayementView.as_view(), name='capture-payment'),
    path('orders/<str:order_number>/',view=OrderDetailView.as_view(),name='order-detail'),
    path('orders/<int:order_id>/create-payment/', view=CreatePaymentView.as_view(), name='create-payment'),
]