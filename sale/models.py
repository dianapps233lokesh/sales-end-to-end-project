from django.db import models

class location(models.Model):
    region=models.CharField(max_length=50)
    country=models.CharField(max_length=50)

class ItemType(models.Model):
    item_type=models.CharField(50)

class Product(models.Model):
    item_type=models.ForeignKey(ItemType,on_delete=models.CASCADE)
    unit_price=models.FloatField()
    unit_cost=models.FloatField()

class Sale(models.Model):
    order_id=models.ForeignKey('order.Order',on_delete=models.CASCADE)
    unit_sold=models.IntegerField()
    total_revenue=models.FloatField()
    total_cost=models.FloatField()
    total_profit=models.FloatField()

