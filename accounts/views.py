from django.shortcuts import render
from .serializers import RegisterSerializer,OTPSerializer
from django.contrib.auth import get_user_model
from .emails import send_otp_via_email
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OTP

User=get_user_model()


class RegisterAPI(APIView):
    
    def post(self,request):
        data=request.data
        serializer=RegisterSerializer(data=data)
        print("=====>", serializer)
        if serializer.is_valid():
            otp=send_otp_via_email(serializer.data['email'])
            print("====>  ")
            OTP.objects.update_or_create(mail=serializer.validated_data['email'],
                                         defaults={
                                             'otp':otp,
                                             'data':serializer.validated_data
                                         })
            return Response({
                'status':200,
                'message':"otp sent successfully",
                'data':serializer.validated_data
            })
        return Response({
            'status':400,
            'message':"invalid data",
            'data':serializer.errors
        })
           
        

class VerifyOTPAPI(APIView):
    def post(self,request):
        email=request.data['email']
        otp=request.data['otp']

        entry=OTP.objects.get(mail=email)
        # serializer=OTPSerializer(entry)
        # print(serializer.data['data'])
        if not entry.is_valid():
            return Response({
                'status':400,
                'message':'OTP expired',
            })
        
        if entry.otp!=otp:
            return Response({
                'status':400,
                'message':'OTP didnot matched'
            })
        serializer = RegisterSerializer(data=entry.data)
        if serializer.is_valid():
            user=serializer.save()
            entry.delete()
            return Response({'status': 200, 'message': 'Registration successful.'})
    
      