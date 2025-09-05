# admin_panel/views.py
from rest_framework import viewsets, permissions
from users.models import CustomUser
from .serializers import AdminUserSerializer

class UserAdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows admin users to be viewed or edited.
    """
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    # --- هذه هي أهم خطوة للأمان ---
    # تسمح فقط للمستخدمين الذين لديهم is_staff=True بالوصول
    permission_classes = [permissions.IsAdminUser]