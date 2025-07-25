import warnings
from google.oauth2.credentials import Credentials
from Calendar.models import AuthInfo
from rest_framework.response import Response
from rest_framework import status
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta
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

def get_free_slots(busy_slots, start_of_day, end_of_day):
    free_slots = []
    if not busy_slots:
        return [(start_of_day, end_of_day)]

    busy_slots = sorted([(datetime.fromisoformat(b['start']), datetime.fromisoformat(b['end'])) for b in busy_slots])

    current = start_of_day
    for start, end in busy_slots:
        if current < start:
            free_slots.append((current, start))     # add free time from current to next meeting start
        current = max(current, end)                 # move current to near meeting end so it can refer to thee next free time

    if current < end_of_day:     #remaining part between end of event and midnighht
        free_slots.append((current, end_of_day))

    return free_slots



def get_busy(service,start_of_day,end_of_day):
        body = {
            "timeMin": start_of_day.isoformat(),
            "timeMax": end_of_day.isoformat(),
            "timeZone": "Asia/Kolkata",
            "items": [{"id": "primary"}]
        }
        resp = service.freebusy().query(body=body).execute()
        return resp['calendars']['primary'].get('busy', [])


def common_time(slots1, slots2, duration_min):
    for s1_start, s1_end in slots1:
        for s2_start, s2_end in slots2:
            start = max(s1_start, s2_start)
            end = min(s1_end, s2_end)
            if (end - start) >= timedelta(minutes=duration_min):
                return (start, start + timedelta(minutes=duration_min))
    return None
