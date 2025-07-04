from django.core.management.base import BaseCommand
from sale.models import location,Product,Sale
from order.models import Order
import datetime

class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        with open('5m_Sales_Records.csv','r') as f:
            i=0
            for line in f:
                line=line.split(',')
                if line[0]=='Region':
                    continue
                dt=datetime.datetime.strptime(line[5],"%m/%d/%Y")
                dt1=datetime.datetime.strptime(line[7],"%m/%d/%Y")
                line[5]=dt.strftime("%Y-%m-%d")
                line[7]=dt1.strftime("%Y-%m-%d")
                print(line)
                print("===",line[1])
                

                loc,created=location.objects.get_or_create(country=line[1],
                                                   defaults={
                                                       'region':line[0]
                                                   })
                print("location object",loc.country)
                print("===1",line[1])


                prod,created=Product.objects.get_or_create(item_type=line[2],defaults={
                    'unit_price':line[-5],
                    'unit_cost':line[-4]
                    })
                print("===2",line[1])
                print("product item type:",line[6])

                # order = 
                ord,created=Order.objects.get_or_create(order_id=line[6],
                                                defaults={'item_type':prod,'order_date':line[5],'ship_date':line[7],'order_priority':line[4],'sales_channel':line[3],'country':loc}
                                                )
                print("===3",line[1])


                sale,created=Sale.objects.get_or_create(order_id=ord,
                                                        defaults=
                                                        {
                                                            'unit_sold':line[-6],'total_revenue':line[-3],'total_cost':line[-2],'total_profit':line[-1][:-2]
                                                        })
              
                # print(line)
                # print(type(line[5]))
                # break
                print(i+1)
                i=i+1
                if i==1000:
                    break

            