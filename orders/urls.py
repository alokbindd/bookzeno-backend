from django.urls import path
from .views import CheckoutView, CreatePaymentView, CapturePayementView

urlpatterns =[
    path('checkout/', view=CheckoutView.as_view(), name='checkout'),
    path('<int:order_id>/create-payment/', view=CreatePaymentView.as_view(), name="create-payment"),
    path('capture-payment/', view=CapturePayementView.as_view(), name="capture-payment"),
    # path('',),
    # path('<int:order_id>/'),
]