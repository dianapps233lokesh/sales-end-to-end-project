from django.shortcuts import render
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from rest_framework.response import Response
from rest_framework.views import APIView
import pickle
from rest_framework import status

class ValidateUser(APIView):
    def get(self,request):
        try:
            scopes = ['https://www.googleapis.com/auth/calendar']
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
            credentials = flow.run_local_server(port=8000)
            pickle.dump(credentials, open("token.pkl", "wb"))
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
    def get(self,request):
        try:
            credentials=pickle.load(open("token.pkl","rb"))
            service=build("calendar","v3",credentials=credentials)
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
    def get(self,request,calendar_id):
        try:
            credentials=pickle.load(open("token.pkl","rb"))
            service=build("calendar","v3",credentials=credentials)
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