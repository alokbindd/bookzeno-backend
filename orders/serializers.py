from rest_framework import serializers

from orders.models import Order, OrderProduct


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

class OrderHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ['id','order_number','order_total','tax','grand_total','status','created_at']
    
class OrderProductSerializers(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    cover_image = serializers.ImageField(source='book.cover_image', read_only=True)

    class Meta:
        model = OrderProduct
        fields = ['id','book_title','cover_image','quantity', 'book_price']


class OrderDetailserializer(serializers.ModelSerializer):
    items = OrderProductSerializers(many=True, read_only=True)
    payments = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id','order_number','status','full_name','email','phone_number','full_address','state','city','pincode','country','order_note','order_total','tax','grand_total','created_at','items','payments']

    def get_payments(self,obj):
        payment = obj.payments.filter(status='completed').first()
        if not payment:
            return None
        
        return {
            "payment_id": payment.payment_id,
            "payment_method": payment.payment_method,
            "amount_paid": payment.amount_paid,
            "status": payment.status,
            "created_at": payment.created_at,
        }