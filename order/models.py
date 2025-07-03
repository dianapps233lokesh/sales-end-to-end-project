from django.db import models

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

class Order(models.Model):
    order_id=models.IntegerField()
    item_type=models.ForeignKey('sale.ItemType',on_delete=models.CASCADE)
    order_date=models.DateField()
    ship_date=models.DateField()
    order_priority=models.CharField(max_length=4, choices=order_priority_choices)
    sales_channel=models.CharField(max_length=10,choices=sales_channel_choices)
    country=models.ForeignKey('sale.location',on_delete=models.CASCADE)