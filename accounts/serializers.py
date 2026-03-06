from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

# import order model for aggregations
from orders.models import Order


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Login with username OR email; reject inactive users."""

    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = (attrs.get('username') or '').strip()
        email = (attrs.get('email') or '').strip()
        password = attrs.get('password')

        if not username and not email:
            raise serializers.ValidationError(
                "Provide either username or email."
            )
        if not password:
            raise serializers.ValidationError("Password is required.")

        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
        if not user and username:
            user = User.objects.filter(username__iexact=username).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError(
                "Account is not activated. Check your email for the activation link."
            )

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.pk,
                'username': user.username,
                'email': user.email,
            },
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=False,
        )
        return user

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        existing = User.objects.filter(email__iexact=value).first()
        if existing and existing.is_active:
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)

class DashboardSerializer(serializers.ModelSerializer):
    # expose calculated values via readonly fields or methods
    total_orders = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=10,decimal_places=2, read_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'total_orders',
            'total_spent',
            'date_joined'
        ]

    # def get_total_orders(self, obj):
    #     # count only completed/paid orders; adjust filter as needed
    #     return Order.objects.filter(user=obj, status='paid').count()

    # def get_total_spent(self, obj):
    #     # sum the grand_total (or order_total) of paid orders
    #     result = Order.objects.filter(user=obj, status='paid').aggregate(
    #         total=Sum('grand_total')
    #     )
    #     return result['total'] or 0