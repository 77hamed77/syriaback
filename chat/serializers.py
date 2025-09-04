# chat/serializers.py
from rest_framework import serializers
from .models import Chat, Message, Feedback

class MessageSerializer(serializers.ModelSerializer):
    # --- أضف هذا السطر ---
    # هذا السطر يخبر المعالج أنه سيستقبل حقلاً اسمه 'message'
    # ولكنه سيقوم بكتابته في حقل 'content' في قاعدة البيانات.
    message = serializers.CharField(source='content', write_only=True)
    # --------------------

    class Meta:
        model = Message
        # --- أضف 'message' إلى الحقول ---
        fields = ['id', 'content', 'is_ai_response', 'created_at', 'message']
        # --- اجعل 'content' للقراءة فقط، لأننا سنكتب عبر 'message' ---
        read_only_fields = ['content']

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at', 'updated_at']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['rating', 'feedback_type', 'comment']