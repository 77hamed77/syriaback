# users/views.py
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, UserSettings
from .serializers import (
    UserSerializer, RegisterSerializer, UserSettingsSerializer, 
    MyTokenObtainPairSerializer, ChangePasswordSerializer
)
from chat.models import Chat, Message
import json
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView

# ========================================================================
# العروض (Views)
# ========================================================================

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UserSettingsView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSettingsSerializer

    def get_object(self):
        settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        return settings

# --- عرض تغيير كلمة المرور (تمت إضافة المنطق الفعلي) ---
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        current_password = serializer.validated_data.get("current_password")
        new_password = serializer.validated_data.get("new_password")

        # التحقق من صحة كلمة المرور الحالية
        if not user.check_password(current_password):
            return Response({"current_password": ["Incorrect password."]}, status=status.HTTP_400_BAD_REQUEST)
        
        # تعيين كلمة المرور الجديدة (سيتم تجزئتها تلقائيًا)
        user.set_password(new_password)
        user.save()
        
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

# --- عرض حذف الحساب ---
class DeleteAccountView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user

# --- عرض تصدير بيانات المستخدم (تمت إضافة المنطق الفعلي) ---
class ExportUserDataView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        # تجميع بيانات الملف الشخصي والإعدادات
        profile_data = UserSerializer(user).data
        settings_data = UserSettingsSerializer(user.settings).data
        
        # تجميع بيانات المحادثات والرسائل
        chats_data = []
        for chat in Chat.objects.filter(user=user):
            messages_data = []
            for message in Message.objects.filter(chat=chat).order_by('created_at'):
                messages_data.append({
                    "content": message.content,
                    "is_ai_response": message.is_ai_response,
                    "created_at": message.created_at.isoformat()
                })
            
            chats_data.append({
                "id": str(chat.id),
                "title": chat.title,
                "created_at": chat.created_at.isoformat(),
                "messages": messages_data
            })

        # بناء الكائن النهائي للتصدير
        data_to_export = {
            "profile": profile_data,
            "settings": settings_data,
            "chats": chats_data
        }
        
        # إنشاء استجابة HTTP مع ترويسات التنزيل
        response = HttpResponse(
            json.dumps(data_to_export, indent=4, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )
        response['Content-Disposition'] = 'attachment; filename="syriagpt_user_data.json"'
        
        return response