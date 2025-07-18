from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OrderSerializer
from rest_framework import status
from rest_framework import permissions
from .models import Order
from utils.logger import logging 
from rest_framework.pagination import PageNumberPagination

class OrderAPI(APIView,PageNumberPagination):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request):
        try:
            logging.info(f"current user is {request.user}")
            serializer=OrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({
                    'message':"Order created successfully",
                    "data":serializer.data
                },
                status=status.HTTP_201_CREATED)
            return Response({
                'message':"data not valid",
                'data':serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message':"Error occurred",
                "data":str(e)
            },
            status=status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,pk):
        try:
            order=Order.objects.get(pk=pk)
        except Exception as e:
            return Response({
                'message':"Order not found",
                "data":str(e)
            },
            status=status.HTTP_404_NOT_FOUND)
        try:
            serializer=OrderSerializer(instance=order,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message':"Order data updated successfully.",
                    'data':serializer.data
                },
                status=status.HTTP_200_OK)
            return Response({
                    'message':"data not valid",
                    'data':serializer.data
            },
            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message':"Error occured",
                "data":str(e)
            },
            status=status.HTTP_400_BAD_REQUEST)


        
    def patch(self,request,pk):
        try:
            order=Order.objects.get(pk=pk)
        except Exception as e:
             return Response({
                'message':"Order not found",
                "data":str(e)
            },
            status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer=OrderSerializer(instance=order,data=request.data,partial=True)
            if serializer.is_valid():
                logging.info(f"into the serializer and requested user is {request.user}")
                serializer.save(user=request.user)
                return Response({
                    'message':"Order data updated successfully.",
                    'data':serializer.data
                },
                status=status.HTTP_200_OK)
            return Response({
                    'message':"data not valid",
                    'data':serializer.data
            },
            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message':"Error occured",
                "data":str(e)
            },
            status=status.HTTP_400_BAD_REQUEST)
            

    def delete(self,request,pk):
        try:
            order=Order.objects.get(pk=pk)
        except Exception as e:
            return Response({
                'message':"Order not found",
                "data":str(e)
            },
            status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response({
            'message':"Order deleted successfully",
            'data':None
        },
        status=status.HTTP_200_OK)
        

    def get(self,request):
        try:
            if request.user.is_superuser or request.user.is_staff:
                orders=Order.objects.all()
            else:
                logging.info(f"current user is {request.user.id} and {type(request.user.id)}")
            
                orders=Order.objects.all().filter(user=request.user.id)
                logging.info(f"orders after filtered out are {orders}")
            paginator=PageNumberPagination()
            paginator.page_size=10
            paginated=paginator.paginate_queryset(orders,request,view=self)
            serializer=OrderSerializer(paginated,many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({
                'message':'error',
                'data':str(e)
            },
            status=status.HTTP_400_BAD_REQUEST)