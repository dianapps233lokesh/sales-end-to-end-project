from django.core.management.base import BaseCommand
from sale.models import location,Product,Sale
from order.models import Order
import datetime
from utils.logger import logging
from utils.exceptions import SaleException
import sys
   
logging.info(f"All imports done successfully.")

class Command(BaseCommand):
    help='Custom dump command for data insert into DB'

    def add_arguments(self, parser):
        parser.add_argument('file_path',type=str,help='Path for CSV file')

    def handle(self,*args,**kwargs):
        file_path=kwargs['file_path']
        with open(file_path,'r') as f:
            i=0
            for line in f:
                try:
                        
                    line=line.split(',')
                    
                    if line[0]=='Region':
                        continue
                    for j in [5,7]:
                        dt=datetime.datetime.strptime(line[j],"%m/%d/%Y")
                        line[j]=dt.strftime("%Y-%m-%d")
                    logging.info(f"line number {i+1} has been read from csv")
                except Exception as e:
                    raise SaleException(e,sys)
                              
                try:

                    loc,created=location.objects.get_or_create(country=line[1],
                                                    defaults={
                                                        'region':line[0]
                                                    })
                    if not created:
                        logging.info(f"{loc.country} already exists into location table. row number {i+1}")
                    else:
                        logging.info(f"{loc.country} added into location table. row number {i+1}")
                except Exception as e:
                    raise SaleException(e,sys)

                try:
                    prod,created=Product.objects.get_or_create(item_type=line[2],defaults={
                        'unit_price':line[-5],
                        'unit_cost':line[-4]
                        })
                    if created:
                        logging.info(f"{prod.item_type} product added into product table. row number{i+1}")
                    else:
                        logging.info(f"{prod.item_type} already exists into product table. row number {i+1}")

                except Exception as e:
                    raise SaleException(e,sys)
                
                try:
                    ord,created=Order.objects.get_or_create(order_id=line[6],
                                                    defaults={'item_type':prod,'order_date':line[5],'ship_date':line[7],'order_priority':line[4],'sales_channel':line[3],'country':loc}
                                                    )
                    if created:
                        logging.info(f"{ord.order_id} order id added into order table. row number{i+1}")
                    else:
                        logging.info(f"{ord.order_id} already exists into order table. row number {i+1}")
                except Exception as e:
                    raise SaleException(e,sys)

                try:
                    sale,created=Sale.objects.get_or_create(order_id=ord,
                                                            defaults=
                                                            {
                                                                'unit_sold':line[-6],'total_revenue':line[-3],'total_cost':line[-2],'total_profit':line[-1][:-2]
                                                            })
                    if created:
                        logging.info(f"{sale.order_id} order id sale record added into sale table. row number{i+1}")
                    else:
                        logging.info(f"{sale.order_id} order id sale record already exists into sale table. row number {i+1}")
                except Exception as e:
                    raise(e,sys)

                print(i+1)
                i=i+1
                if i==1000:
                    break

            