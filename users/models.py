# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    # 1. اجعل البريد الإلكتروني فريدًا ومطلوبًا
    email = models.EmailField(unique=True)
    
    # 2. حدد حقل البريد الإلكتروني كحقل تسجيل الدخول
    USERNAME_FIELD = 'email'
    
    # --- هذا هو السطر الذي تم تعديله ---
    # بما أننا نستخدم البريد الإلكتروني كاسم مستخدم، لم نعد بحاجة إلى طلب اسم مستخدم منفصل
    REQUIRED_FIELDS = []
    # ------------------------------------

    profile_picture = models.URLField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class UserSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=10, default='system')
    language = models.CharField(max_length=10, default='ar')
    email_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.user.email}"