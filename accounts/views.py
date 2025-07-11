from django.shortcuts import render
from .serializers import RegisterSerializer,OTPSerializer,LoginSerializer
from django.contrib.auth import get_user_model
from .emails import send_otp_via_email
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OTP
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

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
       

class LoginAPI(APIView):
    def post(self,request):
        try:
            
            serializer=LoginSerializer(data=request.data)
            print("serialization validaiton:",serializer.is_valid())
            try:
                user=User.objects.get(email=serializer.data['email'])
            except Exception as e:
                return Response({  'status':400,
                        'message':"User not found",
                        'data':str(e)})
            
            user=authenticate(username=user.username, password=serializer.data['password'])
            if user:
                print("user has been authenticated successfully")
                refresh=RefreshToken.for_user(user)
                return Response({
                    'status':200,
                    'message':"Login successful",
                    'tokens':{
                        'refresh_token':str(refresh),
                        'access_token':str(refresh.access_token)
                    }
                })
            else:
                return Response({  'status':400,
                    'message':"wrong credentials provided",
                    'data':serializer.errors
                    })
        except Exception as e:
            return Response({  'status':200,
                        'message':"error",
                        'data':str(e)})
        







