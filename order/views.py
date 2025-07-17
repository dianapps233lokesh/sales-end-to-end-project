from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OrderSerializer
from rest_framework import status
from rest_framework import permissions
from .models import Order
from utils.logger import logging

class OrderAPI(APIView):
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
            

    def delete(self,request):
        pass

    def get(self,request):
        pass
