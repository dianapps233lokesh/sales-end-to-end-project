from django.core.management.base import BaseCommand
from order.models import Order
from utils.logger import logging
import time
from django.contrib.auth import get_user_model
from itertools import islice
import random
logging.info(f"All imports done successfully.")

User=get_user_model()
class Command(BaseCommand):
    help='Custom command for the orders to assign to users randomly'

    def handle(self,*args,**kwargs):
        start=time.time()
        BATCH=10000
        t=0
        i=0
        try:
            users=list(User.objects.filter(is_superuser=False))
            logging.info(f"all the users without super user {users}")
            logging.info(f"top 100 order records from database {list(Order.objects.filter(user__isnull=True)[:100])}")
            while True:
                try:
                    batch=list(Order.objects.filter(user__isnull=True)[:BATCH])  # fetching the orders into batches which have user column null
                except Exception as e:
                    logging.error(f"batch not fetched from db {str(e)}")
                if not batch:
                    break
                for order in batch:
                    order.user=random.choice(users)
                    i+=1
                    print(i)

                Order.objects.bulk_update(batch,['user'])  #bulk_update will update the existing rows where user column will be updated with the random user
                t+=len(batch)
            logging.info(f"Assigned random users successfully. total {t}")
        except Exception as e:
            logging.error(f"error occured {str(e)}")