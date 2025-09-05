# admin_panel/serializers.py
from rest_framework import serializers
from users.models import CustomUser

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # نعرض جميع الحقول المهمة للمشرف
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'date_joined', 'is_staff', 'is_active'
        ]