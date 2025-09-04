from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Django يوفر username, password, email, first_name, last_name
    
    # --- التعديلات هنا ---
    # 1. اجعل البريد الإلكتروني فريدًا ومطلوبًا
    email = models.EmailField(unique=True)
    
    # 2. حدد حقل البريد الإلكتروني كحقل تسجيل الدخول
    USERNAME_FIELD = 'email'
    
    # 3. أزل البريد الإلكتروني من الحقول المطلوبة عند إنشاء مستخدم خارق
    #    (اسم المستخدم لا يزال مطلوبًا بواسطة AbstractUser، لكننا نملأه تلقائيًا)
    REQUIRED_FIELDS = ['username']
    # --------------------

    profile_picture = models.URLField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.email
class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=10, default='system') # light, dark, system
    language = models.CharField(max_length=10, default='ar')
    email_notifications = models.BooleanField(default=True)
    # أضف أي إعدادات أخرى هنا

    def __str__(self):
        return f"Settings for {self.user.email}"