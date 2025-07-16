from django.db import models
import random

order_priority_choices=[
    ('H','H'),
    ('L','L'),
    ('M','M'),
    ('C','C'),
]
sales_channel_choices=[
    ('Online','Online'),
    ('Offline','Offline')
]

def generate_unique_order_id():  #generate random id for the order_id in the Order model because inline random generator generates random value when server starts in terminal
    while True:
        id=random.randint(100000,99999999)
        if not Order.objects.filter(order_id=id).exists():
            return id
        

class Order(models.Model):
    user=models.ForeignKey('accounts.MyUser',on_delete=models.CASCADE,null=True)
    order_id=models.BigIntegerField(primary_key=True,default=generate_unique_order_id)
    item_type=models.ForeignKey('sale.Product',on_delete=models.CASCADE)
    order_date=models.DateField()
    ship_date=models.DateField()
    order_priority=models.CharField(max_length=4, choices=order_priority_choices)
    sales_channel=models.CharField(max_length=10,choices=sales_channel_choices)
    country=models.ForeignKey('sale.location',on_delete=models.CASCADE)