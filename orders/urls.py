from django.urls import path
from .views import CheckoutView, CreatePaymentView, CapturePayementView, OrderHistoryView, OrderDetailView

urlpatterns =[
    path('', view=OrderHistoryView.as_view(), name='order-history'),
    path('<str:order_number>/',view=OrderDetailView.as_view(),name='order-detail'),
    path('checkout/', view=CheckoutView.as_view(), name='checkout'),
    path('<int:order_id>/create-payment/', view=CreatePaymentView.as_view(), name='create-payment'),
    path('capture-payment/', view=CapturePayementView.as_view(), name='capture-payment'),
]