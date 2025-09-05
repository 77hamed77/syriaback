# chat/admin.py
from django.contrib import admin
from .models import Chat, Message, Feedback

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at')
    search_fields = ('user__email', 'title')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'is_ai_response', 'created_at')
    list_filter = ('is_ai_response',)
    search_fields = ('content',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('message', 'rating', 'feedback_type', 'created_at')
    list_filter = ('rating', 'feedback_type')