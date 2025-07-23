import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from utils.logger import logging
from .models import Room,Message
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs

User=get_user_model()

class ChatConsumer(WebsocketConsumer):
    # def connect(self):
    #     user=self.scope['user']
    #     logging.info(f"fetched user is {user}")
    #     logging.info(f"SCOPE: {self.scope['url_route']['kwargs']}")

    #     second_username=self.scope['url_route']['kwargs']['username']
    #     logging.info(f"other user is {second_username}")
    #     try:
    #         second_user=User.objects.get(username=second_username)
    #         logging.info(f"User found in the databse with the name {second_user}")
    #     except Exception as e:
    #         logging.error(f"no user found in the databse with the name {second_user}")
    #         return 
    #     self.room_group_name=f"chat_{user.username}_{second_user}"
    #     logging.info(f"group name is {self.room_group_name}")

    #     self.room,created=Room.objects.get_or_create(name=self.room_group_name)
    #     logging.info(f"created room is {self.room}")
    #     self.room.users.set([user,second_user])
    #     self.room.save()

    #     # logging.info(f"channel name is {self.channel_name}")

    #     async_to_sync(self.channel_layer.group_add)(
    #         self.room_group_name,
    #         self.channel_name
    #     )
    #     self.accept()

    def connect(self):
        '''
        function for establishing web socket connection but having one extra feature than 
        above connect method is that it has authentication for particular user so we can
        see the actual flow of application'''
        # Parse token from query string
        query_string = self.scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        self.scope['user'] = AnonymousUser()  # fallback
        if token:
            try:
                # Validate token
                validated_token = JWTAuthentication().get_validated_token(token)
                user = JWTAuthentication().get_user(validated_token)
                self.scope['user'] = user
            except Exception as e:
                print(f"Token error: {e}")
                self.close()
                return

        user = self.scope["user"]
        if user.is_anonymous:
            self.close()
            return

        # Proceed with rest of the connection logic
        second_username = self.scope["url_route"]["kwargs"]["username"]
        try:
            second_user = User.objects.get(username=second_username)
        except User.DoesNotExist:
            self.close()
            return

        usernames = sorted([user.username, second_user.username])
        self.room_group_name = f"chat_{usernames[0]}_{usernames[1]}"
        logging.info(f"{user.username} joined group {self.room_group_name}")

        self.room, _ = Room.objects.get_or_create(name=self.room_group_name)
        self.room.users.set([user, second_user])
        self.room.save()

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()



    def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        user = self.scope["user"]
        logging.info(f"data is {data} and message is {message} and user is {user}")
        if not message or user.is_anonymous:
            return  # you may send an error or close

        # Optionally save the message to the database here
        Message.objects.create(room=self.room, sender=user, text=message)
        logging.info("message successfullly stored into the database")

        # Broadcast the message to the group with sender info
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",  # handler method name
                "message": message,
                "sender": user.username,
            }
        )


    def chat_message(self, event):
        # Receive a message event and send it WebSocket back to client
        self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "sender": event["sender"],
        }))
        logging.info(f"send data from chat_message function")

