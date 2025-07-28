from django.shortcuts import render
from google_auth_oauthlib.flow import InstalledAppFlow
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import AuthInfo
from utils.logger import logging
from rest_framework.permissions import IsAuthenticated
from utils.utils import getServiceObj,get_busy,get_free_slots,common_time
from datetime import datetime,timedelta
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

    def post(self,request):
        # logging.info(f"date is {date}")
        try:
            logging.info(f"current User id is {request.user}")
            target_email=request.data.get('email')
            date=request.data.get('date')
            duration=request.data.get('duration',60)

            if not target_email or not date:
                logging.error("No email or date provided")
                return Response({
                    'message':"no email or date provided",
                    "data":None
                },
                status=status.HTTP_404_NOT_FOUND) 
            

            tz = pytz.timezone('Asia/Kolkata') 
            date = datetime.strptime(date, "%d-%m-%Y")
            time_min = tz.localize(datetime.combine(date, datetime.min.time()))
            time_max = tz.localize(datetime.combine(date, datetime.max.time()))

            service1=getServiceObj(request.user)
            target_user=AuthInfo.objects.get(user__email=target_email).user_id
            service2=getServiceObj(target_user)
            logging.info(f"Target user id is {target_user}")

            busy1=get_busy(service1,time_min,time_max)
            logging.info(f"My busy schedule: {busy1}")
            busy2=get_busy(service2,time_min,time_max)
            logging.info(f"Target user busy schedule: {busy2}")

            free1=get_free_slots(busy1,time_min,time_max)
            logging.info(f"my free slots: {free1}")
            free2=get_free_slots(busy2,time_min,time_max)
            logging.info(f"target user free slots: {free2}")

            slots = common_time(free1, free2, duration)
            # logging.info()
            if not slots:
                return Response({
                    "message":"no common empty slot found.",
                    "data":None

                },
                status=status.HTTP_404_NOT_FOUND)
            logging.info(f"Common empty slots are {slots}")
            common_slots = [(slot[0].isoformat(), slot[1].isoformat()) for slot in slots]
            logging.info(f"common slots in human readable are {common_slots}")

            return Response({
                'message':"response generated",
                "data":common_slots
            },
            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message':"error occured",
                "data":str(e)
                            },
                            status=status.HTTP_400_BAD_REQUEST)
        
class AppointmentBook(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            logging.info(f"current User id is {request.user}")
            target_email=request.data.get('email')
            date_time=request.data.get('date_time')
            duration=request.data.get('duration',60)

            if not target_email or not date_time:
                logging.error("No email or date provided")
                return Response({
                    'message':"no email or date provided",
                    "data":None
                },
                status=status.HTTP_404_NOT_FOUND) 
            
            tz = pytz.timezone('Asia/Kolkata') 
            start_time = datetime.strptime(date_time, "%d-%m-%Y %H:%M")
            start_time = tz.localize(start_time)  
            end_time = start_time + timedelta(minutes=duration)

            service1=getServiceObj(request.user)
 
            start_meet = start_time.isoformat()
            end_meeting = end_time.isoformat()

            event = {
                'summary': 'Meeting scheduled through code',
                'start': {'dateTime': start_meet, 'timeZone': 'Asia/Kolkata'},
                'end': {'dateTime': end_meeting, 'timeZone': 'Asia/Kolkata'},
                'attendees': [{'email': target_email}],
                'description': 'Auto-scheduled based on free slots.'
            }

            created_event = service1.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()

            logging.info(f"meeting created successfully {created_event}")
            return Response({
                "message":"meeting created successfully",
                "data":{
                'summary': 'Meeting scheduled through code',
                'start': {'dateTime': start_meet, 'timeZone': 'Asia/Kolkata'},
                'end': {'dateTime': end_meeting, 'timeZone': 'Asia/Kolkata'},
                'attendees': [{'email': target_email}],
                'description': 'Auto-scheduled based on free slots.'
            }
            },
            status=status.HTTP_200_OK)


        except Exception as e:
            logging.error(f"{str(e)}")
            return Response({
                "message":"error",
                "data":str(e)
            },
            status=status.HTTP_400_BAD_REQUEST)