from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP
from rest_framework_simplejwt.tokens import RefreshToken
from utils.logger import logging
from rest_framework.exceptions import ValidationError

User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=50,min_length=6,write_only=True)
    confirm_password=serializers.CharField(max_length=50,min_length=6,write_only=True)

    class Meta:
        model=User
        fields=['email','password','confirm_password']
        
    def validate(self,attrs):
        if attrs['password']!=attrs['confirm_password']:
            raise serializers.ValidationError({"password":"password fields didn't match."})
        return attrs
    
    def create(self,validated_data):
        user=User(
            email=validated_data['email'],
            username=validated_data['email'].split('@')[0]
        )

        user.set_password(validated_data['password'])
        user.save()
        return user
    
class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model=OTP
        fields='__all__'


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','password']

class LogoutSerializer(serializers.Serializer):
    refresh=serializers.CharField()

    def validate(self,attr):
        self.token=attr['refresh']
        return attr

    def save(self,**kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception as e:
            return str(e)
        
class ProfileupdateSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True)

    class Meta:
        model=User
        fields=["username","first_name","last_name","email"]
        extra_kwargs={
            'first_name':{'required':True},
            'last_name':{'required':True}
        }

    def validate_email(self,value):
        logging.info("Validate email function called inside serializer")
        user=self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            logging.error(f"Email already in use")
            return ValidationError("Email already in use by user")
        return value
            
        
    def validate_username(self,value):
        logging.info("validate email function called inside serializer")
        user=self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            logging.error(f"username already in use")
            return ValidationError("Username already in use by user")
        return value
        
    def update(self,instance,validated_data):

            instance.first_name=validated_data['first_name']
            instance.last_name=validated_data['last_name']
            instance.email=validated_data['email']
            instance.username=validated_data['username']

            instance.save()

            return instance
