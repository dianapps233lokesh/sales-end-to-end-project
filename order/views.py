from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OrderSerializer
from rest_framework import status
from rest_framework import permissions
import random

class OrderAPI(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request):
        try:
            # order_id=random.randint(1000000,99999999)
            # request.data['order_id']=order_id
            serializer=OrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
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