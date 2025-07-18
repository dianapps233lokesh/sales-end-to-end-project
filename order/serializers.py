from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order
from utils.logger import logging
from rest_framework.exceptions import ValidationError

User=get_user_model()

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'
        read_only_fields=['order_id','user']