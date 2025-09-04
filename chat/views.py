# chat/views.py
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, FeedbackSerializer

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

    def create(self, request, *args, **kwargs):
        # 1. التحقق من صحة رسالة المستخدم وحفظها
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        chat_id = self.kwargs['chat_id']
        try:
            chat = Chat.objects.get(id=chat_id, user=request.user)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)
            
        user_message = serializer.save(chat=chat, is_ai_response=False)

        # 2. التحقق من تهيئة نموذج الذكاء الاصطناعي
        if not gemini_model:
            error_message = "AI service is not configured."
            ai_response_message = Message.objects.create(chat=chat, content=error_message, is_ai_response=True)
            return Response({
                "user_message": MessageSerializer(user_message).data,
                "ai_message": MessageSerializer(ai_response_message).data
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 3. إرسال الرسالة إلى خدمة الذكاء الاصطناعي
        try:
            # (اختياري ولكن موصى به) بناء سجل المحادثة لإعطاء السياق للذكاء الاصطناعي
            history = self.get_queryset().exclude(id=user_message.id)
            gemini_history = [
                {"role": "model" if msg.is_ai_response else "user", "parts": [msg.content]}
                for msg in history
            ]
            
            # بدء محادثة جديدة مع السجل
            chat_session = gemini_model.start_chat(history=gemini_history)
            
            # إرسال الرسالة الجديدة
            response = chat_session.send_message(user_message.content)
            ai_content = response.text

        except Exception as e:
            ai_content = f"An error occurred with the AI service: {str(e)}"
            print(f"Gemini API Error: {e}")

        # 4. حفظ رد الذكاء الاصطناعي في قاعدة البيانات
        ai_message = Message.objects.create(chat=chat, content=ai_content, is_ai_response=True)

        # 5. إرجاع كل من رسالة المستخدم ورد الذكاء الاصطناعي إلى الواجهة الأمامية
        return Response({
            "user_message": MessageSerializer(user_message).data,
            "ai_message": MessageSerializer(ai_message).data
        }, status=status.HTTP_201_CREATED)

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