from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, MessageListView, FeedbackCreateView , ClearHistoryView

router = DefaultRouter()
router.register('', ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:chat_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('messages/<uuid:message_id>/feedback/', FeedbackCreateView.as_view(), name='message-feedback'),
    path('clear-history/', ClearHistoryView.as_view(), name='clear-history'),

]