# chatapp/models.py

from django.db import models
# REMOVE: from django.conf import settings # No longer needed for AUTH_USER_MODEL reference directly here

class Message(models.Model):
    """
    Represents a chat message between two users.
    """
    # CORRECT WAY to reference custom User model in models.py
    sender = models.ForeignKey(
        'users.User', # Use the string 'app_label.ModelName'
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name="Sender"
    )
    receiver = models.ForeignKey(
        'users.User', # Use the string 'app_label.ModelName'
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name="Receiver"
    )
    content = models.TextField(verbose_name="Message Content")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    is_read = models.BooleanField(default=False, verbose_name="Is Read")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        # Order messages by timestamp, oldest first for chat history
        ordering = ['timestamp'] 

    def __str__(self):
        # Ensure sender and receiver are loaded to access username
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."
