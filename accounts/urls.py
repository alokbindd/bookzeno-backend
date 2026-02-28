from django.urls import path
from .views import RegisterView, ActivateAccountView

urlpatterns = [
    path('auth/register/',view=RegisterView.as_view(), name='register'),
    path("auth/activate/<str:uid>/<str:token>/", ActivateAccountView.as_view(), name="activate-account"),
]