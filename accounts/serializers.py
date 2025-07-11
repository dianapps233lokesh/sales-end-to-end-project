from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP

User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)

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
        fields=['email','password',]