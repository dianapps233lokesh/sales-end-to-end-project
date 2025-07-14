from django.shortcuts import render
from .serializers import RegisterSerializer,OTPSerializer,LoginSerializer
from django.contrib.auth import get_user_model
from .emails import send_otp_via_email
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OTP
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from utils.logger import logging

User=get_user_model()


class RegisterAPI(APIView): 
    def post(self,request):
        logging.info("POST method called for register api")
        data=request.data
        serializer=RegisterSerializer(data=data)
        logging.info(f"Serialized incoming data with register serializer {serializer}")
        if serializer.is_valid():
            logging.info("register serializer is valid and otp send method called")
            otp=send_otp_via_email(serializer.data['email'])
            logging.info(f"otp generated and sent to the mail {serializer.validated_data['email']}")
            OTP.objects.update_or_create(mail=serializer.validated_data['email'],
                                         defaults={
                                             'otp':otp,
                                             'data':serializer.validated_data
                                         })
            logging.info(f"mail, otp and user data came from post request saved temporary in OTP Model")
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


        try:
            entry=OTP.objects.get(mail=email)
        except Exception as e:
            return Response({  'status':400,
                    'message':"Invalid email entered",
                    'data':str(e)})

        if not entry.is_valid():
            logging.warning(f"OTP Expired")
            return Response({
                'status':400,
                'message':'OTP expired',
            })
        if entry.otp!=otp:
            logging.warning(f"OTP didn't match")
            return Response({
                'status':400,
                'message':'OTP didnot matched'
            })
        serializer = RegisterSerializer(data=entry.data)

        if serializer.is_valid():
            
            user=serializer.save()
            logging.info(f"User saved into database {user}")
            entry.delete()
            return Response({'status': 200, 'message': 'Registration successful.'})
       

class LoginAPI(APIView):
    def post(self,request):
        try:
            
            serializer=LoginSerializer(data=request.data)
            logging.info(f"serializer data in login api {serializer.data}")
            try:
                user=User.objects.get(email=serializer.data['email'])
            except Exception as e:
                return Response({  'status':400,
                        'message':"User not found",
                        'data':str(e)})
            
            user=authenticate(username=user.username, password=serializer.data['password'])
            if user:
                logging.info("User details authenticated successfully")
                refresh=RefreshToken.for_user(user)
                logging.info(f"Token generated for user")
                return Response({
                    'status':200,
                    'message':"Login successful",
                    'tokens':{
                        'refresh_token':str(refresh),
                        'access_token':str(refresh.access_token)
                    }
                })
            else:
                logging.warning(f"Invalid credentials")
                return Response({  'status':400,
                    'message':"wrong credentials provided",
                    'data':serializer.errors
                    })
        except Exception as e:
            return Response({  'status':400,
                        'message':"error",
                        'data':str(e)})
        
class check(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        return Response("You are authenticated")