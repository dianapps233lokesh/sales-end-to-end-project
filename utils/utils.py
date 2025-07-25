import warnings
from google.oauth2.credentials import Credentials
from Calendar.models import AuthInfo
from rest_framework.response import Response
from rest_framework import status
warnings.filterwarnings('ignore')


from apiclient.discovery import build
from .logger import logging

def getServiceObj(user):
    try:
        try:
            auth=AuthInfo.objects.get(user=user)
        except Exception as e:
            return Response({
                'message':f"no data for user id {user}",
                'data':None
            },
            status=status.HTTP_404_NOT_FOUND)
        creds=Credentials(
            token=auth.access_token,
            refresh_token=auth.refresh_token,
            token_uri=auth.token_uri,
            client_id=auth.client_id,
            client_secret=auth.client_secret,
            scopes=auth.scopes.split(",")
        )
        service=build("calendar","v3",credentials=creds)
        logging.info("service object created successfully")
        return service
    except Exception as e:
        logging.info(f"error occured. No service object returned {str(e)}")