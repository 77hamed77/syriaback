from django.db import models
from users.models import CustomUser
import uuid

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats')
    title = models.CharField(max_length=255, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat {self.id} by {self.user.email}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_ai_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat.id}"

class Feedback(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField() # e.g., 1 for bad, 5 for good
    feedback_type = models.CharField(max_length=50) # e.g., 'helpful', 'unhelpful'
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)