# chat/views.py
from django.http import StreamingHttpResponse
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Chat, Message, Feedback
from .serializers import ChatSerializer, MessageSerializer, FeedbackSerializer

import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

load_dotenv()

# تهيئة الذكاء الاصطناعي
try:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    
    genai.configure(api_key=gemini_api_key)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini AI model configured successfully with 'gemini-1.5-flash'.")
except Exception as e:
    gemini_model = None
    print(f"Error configuring Gemini AI model: {e}")

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat__id=chat_id, chat__user=self.request.user).order_by('created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        chat_id = self.kwargs['chat_id']
        try:
            chat = Chat.objects.get(id=chat_id, user=request.user)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)
            
        user_message = serializer.save(chat=chat, is_ai_response=False)

        if not gemini_model:
            return Response({"error": "AI service is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            # --- الخطوة 1: بناء السجل ---
            history = self.get_queryset().exclude(id=user_message.id)
            gemini_history = [
                {"role": "model" if msg.is_ai_response else "user", "parts": [msg.content]}
                for msg in history
            ]
            chat_session = gemini_model.start_chat(history=gemini_history)
            
            # --- الخطوة 2: محاولة بدء التدفق ---
            response_stream = chat_session.send_message(user_message.content, stream=True)

            # --- دالة مولدة للتدفق الناجح ---
            def stream_generator():
                full_response_content = ""
                try:
                    for chunk in response_stream:
                        if chunk.text:
                            full_response_content += chunk.text
                            yield chunk.text
                finally:
                    if full_response_content:
                        Message.objects.create(chat=chat, content=full_response_content.strip(), is_ai_response=True)
            
            return StreamingHttpResponse(stream_generator(), content_type='text/plain; charset=utf-8')

        # --- الخطوة 3: التقاط الأخطاء وإرجاع استجابة JSON ---
        except google_exceptions.ResourceExhausted as e:
            error_message = "You have exceeded your API quota. Please try again later."
            print(f"Gemini Quota Error: {e}")
            return Response({"detail": error_message}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except Exception as e:
            error_message = "An unexpected error occurred with the AI service."
            print(f"Gemini API Error: {e}")
            return Response({"detail": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================================================
# عرض التقييم (تم تحسينه للسماح بالتحديث)
# ========================================================================
class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        message_id = self.kwargs['message_id']
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise serializers.ValidationError("Message not found.")

        if message.chat.user != self.request.user:
            raise serializers.ValidationError("You do not have permission to give feedback on this message.")

        # --- تعديل حاسم: استخدم update_or_create ---
        # هذا يسمح للمستخدم بتغيير رأيه (مثلاً من إعجاب إلى عدم إعجاب)
        Feedback.objects.update_or_create(
            message=message,
            defaults=serializer.validated_data
        )
        # -----------------------------------------

# ========================================================================
# عرض مسح سجل المحادثات (تمت إضافة المنطق الفعلي)
# ========================================================================
class ClearHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            Chat.objects.filter(user=request.user).delete()
            return Response({"message": "All chat history has been cleared successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)