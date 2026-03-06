from django.urls import path

from .views import (ActivateAccountView, ChangePasswordView,
                    CustomTokenRefreshView, LoginView,
                    PasswordResetConfirmView, PasswordResetRequestView,
                    RegisterView, DashboardView,
                    UserProfileView)

urlpatterns = [
    path('accounts/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('accounts/userprofile/', UserProfileView.as_view(), name='userprofile'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/activate/<str:uid>/<str:token>/', ActivateAccountView.as_view(), name='activate'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('accounts/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('accounts/password-reset-confirm/<str:uid>/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('accounts/token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]