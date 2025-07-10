from django.core.management.base import BaseCommand
from sale.models import location,Product,Sale
from order.models import Order
import datetime
from utils.logger import logging
from utils.exceptions import SaleException
import sys
import concurrent.futures
   
logging.info(f"All imports done successfully.")

class Command(BaseCommand):
    help='Custom dump command for data insert into DB by bulk create'

    def add_arguments(self, parser):
        parser.add_argument('file_path',type=str,help='Path for CSV file')

    def bulkcreate(self,unsaved_list,batch_size):
        location.objects.bulk_create(unsaved_list[0],batch_size=batch_size)
        Product.objects.bulk_create(unsaved_list[1],batch_size=batch_size)
        Order.objects.bulk_create(unsaved_list[2],batch_size=batch_size)
        Sale.objects.bulk_create(unsaved_list[3],batch_size=batch_size)

        

    def handle(self,*args,**kwargs):
        try:
            file_path=kwargs['file_path']
            with open(file_path,'r') as f:
                i=1
                loc,products,sales,orders=[],[],[],[]
                seen_countries = set()
                seen_products = set()
                seen_orders = set()
                seen_sales = set()

                executor = concurrent.futures.ThreadPoolExecutor()
                for line in f:
                    try:     
                        line=line.strip().split(',')
                        
                        if line[0]=='Region':
                            continue
                        for j in [5,7]:
                            dt=datetime.datetime.strptime(line[j],"%m/%d/%Y")
                            line[j]=dt.strftime("%Y-%m-%d")
                        logging.info(f"line number {i} has been read from csv")
                        if line[1] not in seen_countries:
                            loc.append(
                                    location(
                                        region=line[0],
                                        country=line[1]
                                    )
                            )
                            seen_countries.add(line[1])
                        logging.info(f"line number {i} has been inserted into location table.")

                        if line[2] not in seen_products:
                            products.append(
                                    Product(
                                        item_type=line[2],
                                        unit_price=line[-5],
                                        unit_cost=line[-4]
                                    )
                                )
                            seen_products.add(line[2])
                        logging.info(f"line number {i} has been inserted into Product table.")

                        if line[6] not in seen_orders:
                            orders.append(
                                Order(
                                    order_id=line[6],
                                    item_type_id=line[2],order_date=line[5],ship_date=line[7],order_priority=line[4],sales_channel=line[3],country_id=line[1]
                                )
                            )
                            seen_orders.add(line[6])
                        logging.info(f"line number {i} has been inserted into Orders table.")

                        if line[6] not in seen_sales:
                            sales.append(
                                Sale(
                                    order_id_id=line[6],
                                    unit_sold=line[-6],total_revenue=line[-3],total_cost=line[-2],total_profit=line[-1]
                                )
                            )
                            seen_sales.add(line[6])
                        logging.info(f"line number {i} has been inserted into Sales table.")

                        if i%1000==0:
                            unsaved_list=[loc,products,orders,sales]
                            # with concurrent.futures.ThreadPoolExecutor() as executor:
                            executor.submit(self.bulkcreate,unsaved_list,1000)
                            loc,products,sales,orders=[],[],[],[]
                        i=i+1
                        print(i)

                    except Exception as e:
                        logging.error(f"Error occured in the filename {__file__} and the error message is {e}")
                        continue
                    try:
                        if loc or products or orders or sales:
                            executor.submit(self.bulkcreate,[loc,products,orders,sales],1000)
                    except Exception as e:
                        logging.error(f"Error occured in the filename {__file__} and the error message is {e}")
                        continue
                logging.info("All data inserted into DB successfully.")
        except Exception as e:
            raise SaleException(e,sys)
                