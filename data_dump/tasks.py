from celery import shared_task
from sale.models import location, Product, Sale
from order.models import Order
from django.db import transaction

@shared_task
def insert_bulk_chunk(parsed_data):
    loc, products, orders, sales = [], [], [], []

    for entry in parsed_data:
        loc.append(location(**entry["location"]))
        products.append(Product(**entry["product"]))
        orders.append(Order(**entry["order"]))
        sales.append(Sale(**entry["sale"]))

    with transaction.atomic():
        location.objects.bulk_create(loc, ignore_conflicts=True, batch_size=1000)
        Product.objects.bulk_create(products, ignore_conflicts=True, batch_size=1000)
        Order.objects.bulk_create(orders, ignore_conflicts=True, batch_size=1000)
        Sale.objects.bulk_create(sales, ignore_conflicts=True, batch_size=1000)
