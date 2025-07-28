from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order

User=get_user_model()

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'
        read_only_fields=['order_id','user']

class OrderSerializerv2(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['order_id','country','item_type','order_date']
        read_only_fields=['order_id','user']