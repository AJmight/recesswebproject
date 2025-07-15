from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_therapist = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    
    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:20]}"


