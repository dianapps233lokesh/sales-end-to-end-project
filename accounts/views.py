from django.shortcuts import render
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer,ProfileupdateSerializer
from django.contrib.auth import get_user_model
from .emails import send_otp_via_email
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OTP
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from utils.logger import logging
from rest_framework import status

User=get_user_model()

class RegisterAPI(APIView): 
    def post(self,request):
        logging.info("POST method called for register api")
        data=request.data
        serializer=RegisterSerializer(data=data)
        logging.info(f"Serialized incoming data with register serializer")
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
                'message':"otp sent successfully",
                'data':serializer.data
            },status=status.HTTP_200_OK)
        return Response({
            'message':"invalid data",
            'data':serializer.errors
         },status=status.HTTP_400_BAD_REQUEST)
           
        
class VerifyOTPAPI(APIView):
    def post(self,request):
        email=request.data['email']
        otp=request.data['otp']

        try:
            try:
                entry=OTP.objects.get(mail=email)
            except Exception as e:
                return Response({ 
                        'message':"Invalid email entered",
                        'data':None},
                        status=status.HTTP_404_NOT_FOUND)

            if not entry.is_valid():
                logging.warning(f"OTP Expired")
                return Response({
                    'message':'OTP expired',
                    "data":None
                },
                status=status.HTTP_400_BAD_REQUEST)
            if entry.otp!=otp:
                logging.warning(f"OTP didn't match in login api")
                return Response({
                    'message':'OTP didnot matched',
                    "data":None
                },
                status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(email=entry.mail)
            except User.DoesNotExist:
                user = None
            if user:
                serializer = ProfileupdateSerializer(user, data=entry.data, context={'request': request})
                logging.info("profile updater serialized")
                if serializer.is_valid():
                    # print("serializer====",serializer)
                    logging.info("profile updater serialized is valid")
                    user=serializer.save()
                    logging.info(f"User updated into database {user}")
                    entry.delete()
                    return Response({
                    'message': 'Updation successful.',
                    'data': ProfileupdateSerializer(user).data
                }, status=status.HTTP_200_OK)

            else:        
                serializer = RegisterSerializer(data=entry.data)
                if serializer.is_valid():
                    user=serializer.save()
                    logging.info(f"User created into database {user}")
                    entry.delete()
                    return Response({ 
                        'message': 'Registration successful',
                        'data':user
                        },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({ 
                        'message': 'error',
                        'data':str(e)
                        },status=status.HTTP_400_BAD_REQUEST)
        

class LoginAPI(APIView):
    def post(self,request):
        try:
          
            try:
                logging.info("Enter into the if block of serializer valid")
                user=User.objects.get(email=request.data['email'])
            except Exception as e:
                return Response({ 'message':f"User not found for {request.data['email']}",
                        'data':str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        
            user=authenticate(username=user.username, password=request.data['password'])
            if user:
                logging.info("User details authenticated successfully")
                refresh=RefreshToken.for_user(user)
                logging.info(f"Token generated for user")
      
                return Response({
                    "message":"Login Successful",
                    "data":{
                        "access_token":str(refresh.access_token),
                        "refresh_token":str(refresh)
                    }
                },status=status.HTTP_200_OK)
            else:
                logging.warning(f"Invalid credentials")
                return Response({ 'message':"wrong credentials provided",
                                 'data':None
                    },status=status.HTTP_404_NOT_FOUND)
          
        except Exception as e:
            return Response(
                { 
                        'message':"error occurred",
                        'data':str(e)
                },status=status.HTTP_400_BAD_REQUEST)
        
class check(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        return Response("You are authenticated")

class LogoutAPI(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        try:
            serializer=LogoutSerializer(data=request.data)
        
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'message':"Refresh Token blacklisted successfully",
                        'data':None
                    },
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {
                    'message':"Can't assign refresh token to the token attr",
                    "data":serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({
                'message':"Error Occured",
                "data":str(e)
            },
            status=status.HTTP_400_BAD_REQUEST)



class UpdateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):

        user = request.user
        serializer = ProfileupdateSerializer(user, data=request.data, context={'request': request})

        if serializer.is_valid():
            otp=send_otp_via_email(serializer.validated_data['email'])
            logging.info(f"serializer validated data in put: {serializer.validated_data}")
            logging.info(f"mail for user {serializer.data['email']}")
            OTP.objects.update_or_create(mail=serializer.data['email'],
                                         defaults={
                                             'otp':otp,
                                             'data':serializer.validated_data
                                         })
            # serializer.save()
            return Response({
                "message": "OTP generated successfully for fully update",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Validation failed",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request):
    #     user = request.user
    #     serializer = ProfileupdateSerializer(user, data=request.data, partial=True, context={'request': request})

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({
    #             "message": "Profile updated successfully",
    #             "data": serializer.data
    #         }, status=status.HTTP_200_OK)

    #     return Response({
    #         "message": "Validation failed",
    #         "data": serializer.errors
    #     }, status=status.HTTP_400_BAD_REQUEST)