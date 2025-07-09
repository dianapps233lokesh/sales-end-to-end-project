from django.core.management.base import BaseCommand
from data_dump.tasks import insert_bulk_chunk
import datetime
from itertools import islice
import time
from utils.logger import logging

logging.info(f"all imports done successfully.")

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
        except Exception as e:
            logging.error("error occurred in {__file__} in parse_line function")
            return {"error":e}

    def handle(self, *args, **kwargs):
      
        start = time.time()
        file_path = kwargs['file_path']
        BATCH = 10000
        try:
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
    
                    if parsed_batch:
                        insert_bulk_chunk.delay(parsed_batch)
            end = time.time()
            print(f"Tasks dispatched. Total time: {end - start:.2f} seconds")
        except Exception as e:
            logging.error(f"error is {e}")
            return None
