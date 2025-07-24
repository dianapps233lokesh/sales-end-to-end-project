from django.db import models

class CreateTrack(models.Model):
    created_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class Room(CreateTrack):
    name=models.CharField(max_length=255,unique=True)
    users=models.ManyToManyField('accounts.MyUser')

    def __str__(self):
        return f"Room no. {self.id}"


class Message(CreateTrack):
    room=models.ForeignKey('Room',on_delete=models.CASCADE)
    sender=models.ForeignKey('accounts.MyUser',on_delete=models.CASCADE)
    text=models.TextField()

    def __str__(self):
        return f"sender {self.sender} and message is {self.text}"