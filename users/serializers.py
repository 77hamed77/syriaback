# users/serializers.py
from rest_framework import serializers
from .models import CustomUser, UserSettings
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

# ========================================================================
# 1. معالج مخصص لتسجيل الدخول
# ========================================================================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # نستخدم النسخة المعدلة من UserSerializer التي تحتوي على الإحصائيات
        serializer = UserSerializer(self.user)
        data['user'] = serializer.data
        return data

# ========================================================================
# 2. معالج بيانات المستخدم (تمت إضافة حقول الإحصائيات)
# ========================================================================
class UserSerializer(serializers.ModelSerializer):
    conversations_count = serializers.SerializerMethodField()
    active_days = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        # --- أضف 'username' إلى قائمة الحقول ---
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 
            'phone_number', 'date_joined',
            'conversations_count', 'active_days'
        ]
        # --- أضف 'username' إلى حقول القراءة فقط ---
        read_only_fields = ['email', 'date_joined', 'username']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def get_conversations_count(self, obj):
        return obj.chats.count()

    def get_active_days(self, obj):
        if not obj.date_joined:
            return 0
        delta = timezone.now() - obj.date_joined
        return delta.days + 1

# ========================================================================
# 3. معالج إنشاء حساب جديد
# ========================================================================
class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone_number')
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already in use."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', None)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# ========================================================================
# 4. معالج تغيير كلمة المرور
# ========================================================================
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"new_password": "New passwords must match."})
        validate_password(data['new_password'])
        return data

# ========================================================================
# 5. معالج إعدادات المستخدم
# ========================================================================
class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['theme', 'language', 'email_notifications']