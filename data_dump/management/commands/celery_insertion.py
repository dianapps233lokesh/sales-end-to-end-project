from django.core.management.base import BaseCommand
from data_dump.tasks import insert_bulk_chunk
import datetime
from itertools import islice
import time
# from celery import shared_task
from sale.models import location, Product, Sale
from order.models import Order


# @shared_task
# def insert_bulk_chunk(parsed_data):
#     loc, products, orders, sales = [], [], [], []

#     for entry in parsed_data:
#         loc.append(location(**entry["location"]))
#         products.append(Product(**entry["product"]))
#         orders.append(Order(**entry["order"]))
#         sales.append(Sale(**entry["sale"]))

    
#     location.objects.bulk_create(loc, ignore_conflicts=True, batch_size=1000)
#     Product.objects.bulk_create(products, ignore_conflicts=True, batch_size=1000)
#     Order.objects.bulk_create(orders, ignore_conflicts=True, batch_size=1000)
#     Sale.objects.bulk_create(sales, ignore_conflicts=True, batch_size=1000)

class Command(BaseCommand):
    help = 'Dispatch CSV chunks to Celery for parallel bulk_create'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to CSV file')

    def parse_line(self, line):
        try:
            line = line.strip().split(',')
            if line[0] == 'Region':
                return None

            for j in [5, 7]:
                dt = datetime.datetime.strptime(line[j], "%m/%d/%Y")
                line[j] = dt.strftime("%Y-%m-%d")

            return {
                "location": {"region": line[0], "country": line[1]},
                "product": {"item_type": line[2], "unit_price": line[-5], "unit_cost": line[-4]},
                "order": {
                    "order_id": line[6],
                    "item_type_id": line[2],
                    "order_date": line[5],
                    "ship_date": line[7],
                    "order_priority": line[4],
                    "sales_channel": line[3],
                    "country_id": line[1]
                },
                "sale": {
                    "order_id_id": line[6],
                    "unit_sold": line[-6],
                    "total_revenue": line[-3],
                    "total_cost": line[-2],
                    "total_profit": line[-1]
                }
            }
        except Exception:
            return None

    def handle(self, *args, **kwargs):
        i=0
        start = time.time()
        file_path = kwargs['file_path']
        BATCH = 10000

        with open(file_path, 'r') as f:
            while True:
                lines_chunk = list(islice(f, BATCH))
                if not lines_chunk:
                    break

                parsed_batch = []

                for line in lines_chunk:
                    parsed = self.parse_line(line)
                    if parsed:
                        parsed_batch.append(parsed)
                    i+=1
                    print(i)

                if parsed_batch:
                    insert_bulk_chunk.delay(parsed_batch)

        end = time.time()
        print(f"Tasks dispatched. Total time: {end - start:.2f} seconds")
