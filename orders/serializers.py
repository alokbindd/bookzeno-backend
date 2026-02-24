from rest_framework import serializers

class CheckoutSerializer(serializers.Serializer):
    first_name      = serializers.CharField(max_length=50)
    last_name       = serializers.CharField(max_length=50)
    email           = serializers.EmailField()
    phone_number    = serializers.CharField(max_length=15)
    address_line_1  = serializers.CharField(max_length=50)
    address_line_2  = serializers.CharField(max_length=50, required=False , allow_blank=True,)
    state           = serializers.CharField(max_length=20)
    city            = serializers.CharField(max_length=20)
    pincode         = serializers.CharField(max_length=20)
    country         = serializers.CharField(max_length=20)
    order_note      = serializers.CharField(required=False, allow_blank=True)