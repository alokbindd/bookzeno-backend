from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.conf import settings

from core.utils import success_response, error_response
from accounts.tokens import account_activation_token
from accounts.serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
)


def _send_activation_email(user):
    """Send activation email to user."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    mail_subject = "Activate your account"
    activation_link = f"{settings.FRONTEND_URL}activate/{uid}/{token}/"
    message = render_to_string(
        'accounts/account_verification_email.html',
        {"user": user, "activation_link": activation_link},
    )
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        # Resend activation if email exists and user is inactive
        if email:
            inactive_user = User.objects.filter(
                email__iexact=email, is_active=False
            ).first()
            if inactive_user:
                _send_activation_email(inactive_user)
                return success_response(
                    message="If your account exists, an activation link has been sent."
                )

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            _send_activation_email(user)
            return success_response(
                data=RegisterSerializer(user).data,
                message="Registration successful. Check your email to activate.",
            )
        return error_response(errors=serializer.errors)

class ActivateAccountView(APIView):
    """GET /api/accounts/activate/<uid>/<token>/ — redirects to frontend."""

    def get(self, request, uid, token):
        from django.shortcuts import redirect

        base_url = settings.FRONTEND_URL.rstrip('/')
        login_path = f"{base_url}/login"

        if not uid or not token:
            return redirect(f"{login_path}?activated=false")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (ValueError, TypeError, OverflowError, User.DoesNotExist):
            return redirect(f"{login_path}?activated=false")

        if user.is_active:
            return redirect(f"{login_path}?already=true")

        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect(f"{login_path}?activated=true")

        return redirect(f"{login_path}?activated=false")


class LoginView(TokenObtainPairView):
    """POST /api/accounts/login/ — JWT login with username OR email."""
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """POST /api/accounts/token/refresh/ — Refresh JWT access token."""
    pass


class ChangePasswordView(APIView):
    """POST /api/accounts/change-password/ — Change password (JWT required)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return success_response(message="Password changed successfully.")
        return error_response(errors=serializer.errors)


def _send_password_reset_email(user):
    """Send password reset link to user."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    mail_subject = "Reset your password"
    reset_link = f"{settings.FRONTEND_URL}reset-password/{uid}/{token}/"
    message = render_to_string(
        'accounts/password_reset_email.html',
        {"user": user, "reset_link": reset_link},
    )
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()


class PasswordResetRequestView(APIView):
    """POST /api/accounts/password-reset/ — Request reset link (no enumeration)."""

    def post(self, request):
        email = request.data.get('email', '').strip()
        # Always return same message to avoid user enumeration
        if email:
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user:
                _send_password_reset_email(user)
        return success_response(
            message="If an account exists with this email, a reset link has been sent."
        )


class PasswordResetConfirmView(APIView):
    """POST /api/accounts/password-reset-confirm/<uid>/<token>/ — Set new password."""

    def post(self, request, uid, token):
        if not uid or not token:
            return error_response(message="Invalid reset link.")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (ValueError, TypeError, OverflowError, User.DoesNotExist):
            return error_response(message="Invalid or expired reset link.")

        if not account_activation_token.check_token(user, token):
            return error_response(message="Invalid or expired reset link.")

        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return success_response(message="Password reset successfully.")
        return error_response(errors=serializer.errors)