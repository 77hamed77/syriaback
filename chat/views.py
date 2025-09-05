# chat/views.py
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, FeedbackSerializer
from django.http import StreamingHttpResponse

# --- استيرادات جديدة للذكاء الاصطناعي والإعدادات ---
import os
from dotenv import load_dotenv
import google.generativeai as genai
# ----------------------------------------------------

# --- تهيئة الذكاء الاصطناعي ---
# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# قم بتكوين واجهة برمجة تطبيقات Gemini باستخدام مفتاحك
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    # اختر النموذج الذي تريد استخدامه
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini AI model configured successfully with 'gemini-1.5-flash'.")
except Exception as e:
    gemini_model = None
    print(f"Error configuring Gemini AI model: {e}")
# --------------------------------

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ========================================================================
# عرض الرسائل (تمت إضافة منطق الذكاء الاصطناعي)
# ========================================================================
class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat__id=chat_id, chat__user=self.request.user).order_by('created_at')

    # --- تم تعديل هذه الدالة بالكامل ---
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

        # --- دالة مولدة (Generator) لمعالجة الرد المتدفق ---
        def stream_gemini_response():
            full_response_content = ""
            try:
                history = self.get_queryset().exclude(id=user_message.id)
                gemini_history = [
                    {"role": "model" if msg.is_ai_response else "user", "parts": [msg.content]}
                    for msg in history
                ]
                
                chat_session = gemini_model.start_chat(history=gemini_history)
                
                # استخدم stream=True للحصول على الرد بشكل متدفق
                response_stream = chat_session.send_message(user_message.content, stream=True)

                for chunk in response_stream:
                    if chunk.text:
                        full_response_content += chunk.text
                        yield chunk.text # إرسال كل جزء إلى الواجهة الأمامية

            except Exception as e:
                error_text = f"An error occurred with the AI service: {str(e)}"
                full_response_content = error_text
                yield error_text
                print(f"Gemini API Error: {e}")
            
            finally:
                # بعد انتهاء التدفق، قم بحفظ الرسالة الكاملة في قاعدة البيانات
                if full_response_content:
                    Message.objects.create(chat=chat, content=full_response_content.strip(), is_ai_response=True)

        # إرجاع استجابة متدفقة
        return StreamingHttpResponse(stream_gemini_response(), content_type='text/plain')
    
class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        message_id = self.kwargs['message_id']
        message = Message.objects.get(id=message_id)
        if message.chat.user == self.request.user:
            serializer.save(message=message)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

# ========================================================================
# عرض مسح سجل المحادثات (تمت إضافة المنطق الفعلي)
# ========================================================================
class ClearHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # ابحث عن جميع محادثات المستخدم الحالي وقم بحذفها
            # سيؤدي هذا إلى حذف جميع الرسائل المرتبطة بها تلقائيًا بسبب on_delete=models.CASCADE
            Chat.objects.filter(user=request.user).delete()
            return Response({"message": "All chat history has been cleared successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)