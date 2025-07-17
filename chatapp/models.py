from django.db import models
from django.conf import settings # To reference AUTH_USER_MODEL


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp'] # Order messages by time
        verbose_name = "Message"
        verbose_name_plural = "Messages"
    
    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."
