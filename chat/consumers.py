import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from utils.logger import logging
from .models import Room,Message
from django.contrib.auth import get_user_model

User=get_user_model()

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        user=self.scope['user']
        logging.info(f"fetched user is {user}")
        logging.info(f"SCOPE: {self.scope['url_route']['kwargs']}")

        second_username=self.scope['url_route']['kwargs']['username']
        logging.info(f"other user is {second_username}")
        try:
            second_user=User.objects.get(username=second_username)
            logging.info(f"User found in the databse with the name {second_user}")
        except Exception as e:
            logging.error(f"no user found in the databse with the name {second_user}")
            return 
        self.room_group_name=f"chat_{user.username}_{second_user}"
        logging.info(f"group name is {self.room_group_name}")

        self.room,created=Room.objects.get_or_create()
        logging.info(f"created room is {self.room}")
        self.room.users.set([user,second_user])
        self.room.save()

        # logging.info(f"channel name is {self.channel_name}")

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()


    # def receive(self, text_data):
    #     data = json.loads(text_data)
    #     message = data.get("message", "").strip()
    #     user = self.scope["user"]
    #     logging.info(f"data is {data} and message is {message} and user is {user}")
    #     if not message or user.is_anonymous:
    #         return  # you may send an error or close

    #     # Optionally save the message to the database here
    #     room = Room.objects.get(users__username=user.username, users__username=other_username)
    #     Message.objects.create(room=room, sender=user, text=message)

    #     # Broadcast the message to the group with sender info
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             "type": "chat_message",  # handler method name
    #             "message": message,
    #             "sender": user.username,
    #         }
    #     )
    # def chat_message(self, event):
    #     # Receive a message event and send it WebSocket back to client
    #     self.send(text_data=json.dumps({
    #         "type": "chat",
    #         "message": event["message"],
    #         "sender": event["sender"],
    #     }))
    #     logging.info(f"send data from chat_message function")


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         user = self.scope["user"]
#         other_username = self.scope['url_route']['kwargs']['room_name']
#         # Determine a consistent room name (e.g. alphabetical)
#         users_sorted = sorted([user.username, other_username])
#         self.room_group_name = f"chat_{users_sorted[0]}_{users_sorted[1]}"

#         # Join the room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#         self.accept()


