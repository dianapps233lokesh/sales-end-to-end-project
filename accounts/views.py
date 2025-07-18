from django.shortcuts import render
from .serializers import RegisterSerializer,LogoutSerializer,ProfileupdateSerializer,CreateUserSerializer,UserSerializer
from django.contrib.auth import get_user_model
from .emails import send_otp_via_email
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OTP
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from utils.logger import logging
from rest_framework import status
from django.contrib.auth.hashers import make_password

User=get_user_model()

class RegisterAPI(APIView): 
    def post(self,request):
        logging.info("POST method called for register api")
        data=request.data
        serializer=RegisterSerializer(data=data)
        logging.info(f"Serialized incoming data with register serializer")
        if serializer.is_valid():
            logging.info("register serializer is valid and otp send method called")
            password = make_password(serializer.validated_data['password'])
            otp=send_otp_via_email(serializer.data['email'])
            logging.info(f"your otp is {otp}")
            logging.info(f"otp generated and sent to the mail {serializer.validated_data['email']}")
            OTP.objects.update_or_create(mail=serializer.validated_data['email'],
                                         defaults={
                                             'otp':otp,
                                             'data':{
                                                 'email':serializer.validated_data['email'],
                                                 'password':password
                                             }
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
                serializer = ProfileupdateSerializer(user, data=entry.data,partial=True,context={'request': request})
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
                serializer = CreateUserSerializer(data=entry.data)
                if serializer.is_valid():
                    user=serializer.save()
                    logging.info(f"User created into database {user}")
                    entry.delete()
                    refresh=RefreshToken.for_user(user)
                    return Response({ 
                        'message': 'Registration successful',
                        'data':{
                            'access_token':str(refresh.access_token),
                            'refresh_token':str(refresh)
                        },
                        },status=status.HTTP_201_CREATED)
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
                user=User.objects.get(email=request.data['email'])  #getting user based upon email from db because in authenticate username is required not email
            except Exception as e:
                return Response({ 'message':f"User not found for {request.data['email']}",
                        'data':str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        
            user=authenticate(username=user.username, password=request.data['password'])  #returns authenticated user if exists or none
            if user:
                logging.info("User details authenticated successfully")
                refresh=RefreshToken.for_user(user)    #manually token generated here
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

class LogoutAPI(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        try:
            serializer=LogoutSerializer(data=request.data)
        
            if serializer.is_valid():   
                serializer.save()   # token blacklisted into serializer save method
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
    '''PUT Here is updating all the fields including email thus required email verificaiton'''
    def put(self, request):
        logging.info(f"requested data:{request.data}")
        user = request.user
        logging.info(f"Email of current user is {user.email}")
        logging.info(f"Email of provided by user for update is {request.data['email']}")
        serializer = ProfileupdateSerializer(user, data=request.data, context={'request': request})

        if serializer.is_valid():
            otp=send_otp_via_email(serializer.validated_data['email'])  # OTP Verification function called
            logging.info(f"serializer validated data in put: {serializer.validated_data}")
            logging.info(f"mail for user {serializer.data['email']}")
            OTP.objects.update_or_create(mail=serializer.data['email'],
                                         defaults={
                                             'otp':otp,
                                             'data':serializer.validated_data
                                         })
            return Response({
                "message": "OTP generated successfully for fully update",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Validation failed",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    '''If email is updated into patch then email verification required otherwise details updated directly without email verification'''
    def patch(self,request):
        logging.info("Entered into patch request")
        user=request.user
        current_email=user.email
        requested_email=request.data.get('email',None)
        serializer=ProfileupdateSerializer(user,data=request.data,partial=True,context={'request':request})
        logging.info("Serializer created for the patch api user update")
        try:
            if serializer.is_valid():
                logging.info("profile update serializer is valid into the patch api")
                if requested_email and requested_email!=current_email:
                    '''When updating email, verification required because user may enter invalid email'''
                    otp=send_otp_via_email(serializer.validated_data['email'])  #OTP verification method called for email update
                    logging.info(f"serializer validated data in patch: {serializer.validated_data}")
                    logging.info(f"mail for user {serializer.data['email']}")
                    OTP.objects.update_or_create(mail=serializer.data['email'],     #saving request data into otp relation temporarily
                                            defaults={
                                                'otp':otp,
                                                'data':serializer.validated_data
                                            })
                    return Response({
                    "message": "OTP generated successfully for partial update",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
                elif requested_email and requested_email==current_email:
                    return Response({
                        'message':"This email is already in use",
                        'data':serializer.validated_data
                    },
                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    '''
                    No OTP Verification required thus directly updating into the database
                    '''
                    logging.info("into the else block and next line is serializer save methiod")
                    serializer.save()
                    logging.info("serializer saved successfully")
                    return Response({
                        'message':"profile updated for user without email verified",
                        "data":serializer.data
                    },
                    status=status.HTTP_200_OK)
            return Response({
                'message':"Serializer not valid",
                "data":None
            },
            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message":"error occured",
                "data":str(e)
            },
            status=status.HTTP_400_BAD_REQUEST)


class Userlist(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):
        try:
            users=User.objects.filter(is_superuser=False)
            serializer=UserSerializer(users,many=True)
            return Response({
                'message':"All the users fetched successfully",
                "data":serializer.data
            },
            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message':"error",
                "data":str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActivateDeactivateView(APIView):
    permission_classes=[IsAdminUser]

    def post(self,request,user_id):
        try:
            user=User.objects.get(id=user_id)
        except Exception as e:
            return Response({
                'message':"User with this user id not found",
                "data":str(e)
            },
            status=status.HTTP_404_NOT_FOUND)
        logging.info(f"user active status {user.is_active}")
        try:
            if user.is_active:
                user.is_active=False
                logging.info("user was active and now deactivated")
            else:
                user.is_active=True
                logging.info("User was deactive and now activated ")
            user.save()
            return Response({
                'message':"User active status toggled successfully",
                'data':{
                    "User active status":user.is_active
                }
            },
            status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                    'message':"Error",
                    'data':str(e)
                },
                status=status.HTTP_400_BAD_REQUEST)