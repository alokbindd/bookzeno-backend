from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email','password','first_name','last_name',]

    def create(self, validate_data):
        user = User.objects.create_user(
            username    = validate_data['username'],
            email       = validate_data['email'],
            password    = validate_data['password'],
            first_name  = validate_data.get('first_name',''),
            last_name   = validate_data.get('last_name',''),
        )
        return user