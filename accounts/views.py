from core.utils import success_response, error_response
from accounts.serializers import RegisterSerializer
from rest_framework.decorators import APIView
from accounts.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.shortcuts import redirect

class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
        
            mail_subject = "Proceed to activate your account"
            activation_link = f"{settings.FRONTEND_URL}activate/{uid}/{token}/"
            message = render_to_string('accounts/account_verification_email.html',{
                "user": user,
                "activation_link": activation_link
            })
            to_email = user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            serializer = RegisterSerializer(user)
            return success_response(data=serializer.data)
        return error_response(errors=serializer.errors)

class ActivateAccountView(APIView):

    def get(self, request, uid, token):

        if not uid or not token:
            return error_response(message="Invalid activation data")
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

        except (ValueError, TypeError, OverflowError, User.DoesNotExist):
            return error_response(message="Invalid activation link")
        
        if user.is_active == True:
            return success_response(message="Account already activated")
        
        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return success_response(message="Account activated successfully") 
            # return redirect("http://localhost:3000/login?activated=true")
        return error_response(message="Activation link expired or invalid")