from django.shortcuts import render
from google_auth_oauthlib.flow import InstalledAppFlow
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import AuthInfo
from utils.logger import logging
from rest_framework.permissions import IsAuthenticated
from utils.utils import getServiceObj
from datetime import datetime
import pytz


class ValidateUser(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            scopes = ['https://www.googleapis.com/auth/calendar']
            logging.info("get method called")
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
            logging.info("flow created successfully")
            credentials = flow.run_local_server(port=5000,access_type='offline',prompt='consent',include_granted_scopes='true')
            logging.info("credentials generated successfully")
                       
            AuthInfo.objects.update_or_create(user=request.user,defaults=
                                              {
                        "access_token":credentials.token,"refresh_token":credentials.refresh_token,"expiry":credentials.expiry,
                        "token_uri":credentials.token_uri,"client_id":credentials.client_id,"client_secret":credentials.client_secret,"scopes":','.join(credentials.scopes)
                                    })
         
            logging.info("data saved into database successfully")
            return Response({
                'message':"user credentials generated",
                'data':str(credentials)
            },status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'message':"error",
                'data':str(e)
            },status=status.HTTP_401_UNAUTHORIZED)

class GetCalendars(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:          
            service=getServiceObj(user=request.user)
            result = service.calendarList().list().execute()
            return Response({
                'message':"all the calendars fetched",
                "data":result
            },
            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message':"error",
                'data':str(e)
            },status=status.HTTP_401_UNAUTHORIZED)
        
class GetEvents(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,calendar_id):
        try:
            service=getServiceObj(user=request.user)
            result = service.events().list(calendarId=calendar_id).execute()
            return Response({
                'message':"all the calendars fetched",
                "data":result
            },
            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message':"error",
                'data':str(e)
            },status=status.HTTP_401_UNAUTHORIZED)
        
class GetFreeSlots(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request,date):
        logging.info(f"date is {date}")
        try:
            tz = pytz.timezone('Asia/Kolkata') 
            date = datetime.strptime(date, "%Y-%m-%d")
            time_min = tz.localize(datetime.combine(date, datetime.min.time())).isoformat()
            time_max = tz.localize(datetime.combine(date, datetime.max.time())).isoformat()


            service=getServiceObj(user=request.user)

            body = {
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "timeZone": "Asia/Kolkata",
                    "items": [{"id": "primary"}]
                }
            
            resp=service.freebusy().query(body=body).execute()
            return Response({
                'message':"response generated",
                "data":resp['calendars']['primary']
            },
            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message':"error occured",
                "data":str(e)
                            },
                            status=status.HTTP_400_BAD_REQUEST)
        
class AppointmentBook(APIView):
    def get(self,request):
        pass


    