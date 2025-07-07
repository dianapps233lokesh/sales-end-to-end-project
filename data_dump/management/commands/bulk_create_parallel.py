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
    k=0
    help='Custom dump command for data insert into DB by bulk create'
 

    def add_arguments(self, parser):
        parser.add_argument('file_path',type=str,help='Path for CSV file')

    def bulkcreate(self,unsaved_list,batch_size):
        location.objects.bulk_create(unsaved_list[0],batch_size=batch_size)
        Product.objects.bulk_create(unsaved_list[1],batch_size=batch_size)
        Order.objects.bulk_create(unsaved_list[2],batch_size=batch_size)
        Sale.objects.bulk_create(unsaved_list[3],batch_size=batch_size)

    def parse_line(self, line):
        try:
            line = line.strip().split(',')
            if line[0] == 'Region':
                return None  # Skip header

            for j in [5, 7]:
                dt = datetime.datetime.strptime(line[j], "%m/%d/%Y")
                line[j] = dt.strftime("%Y-%m-%d")

            loc_obj = location(region=line[0], country=line[1])
            product_obj = Product(item_type=line[2], unit_price=line[-5], unit_cost=line[-4])
            order_obj = Order(
                order_id=line[6],
                item_type_id=line[2],
                order_date=line[5],
                ship_date=line[7],
                order_priority=line[4],
                sales_channel=line[3],
                country_id=line[1]
            )
            sale_obj = Sale(
                order_id_id=line[6],
                unit_sold=line[-6],
                total_revenue=line[-3],
                total_cost=line[-2],
                total_profit=line[-1][:-2]
            )
            k+=1
            print(k)
            return (loc_obj, product_obj, order_obj, sale_obj, line[1], line[2], line[6])
        except Exception as e:
            raise SaleException(e,sys)

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        BATCH = 500000

        loc, products, orders, sales = [], [], [], []
        seen_countries = set()
        seen_products = set()
        seen_orders = set()
        seen_sales = set()

        parse_executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        insert_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                # print(lines)

            i = 0
            results = parse_executor.map(self.parse_line, lines)

            for result in results:
                if not result:
                    continue

                loc_obj, product_obj, order_obj, sale_obj, country, product, order_id = result

                if country not in seen_countries:
                    loc.append(loc_obj)
                    seen_countries.add(country)

                if product not in seen_products:
                    products.append(product_obj)
                    seen_products.add(product)

                if order_id not in seen_orders:
                    orders.append(order_obj)
                    seen_orders.add(order_id)

                if order_id not in seen_sales:
                    sales.append(sale_obj)
                    seen_sales.add(order_id)

                i += 1
                if i % BATCH == 0:
                    insert_executor.submit(self.bulk_insert, loc.copy(), products.copy(), orders.copy(), sales.copy())
                    loc.clear()
                    products.clear()
                    orders.clear()
                    sales.clear()
                    logging.info(f"Processed {i} lines...")
                print(i)

        except Exception as e:
            raise SaleException(e, sys)