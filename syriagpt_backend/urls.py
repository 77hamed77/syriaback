# syriagpt_backend/urls.py
from django.contrib import admin
from django.urls import path, include
# --- التعديلات هنا ---
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import MyTokenObtainPairView # <-- استيراد العرض المخصص بدلاً من الافتراضي
# --------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- هذا هو السطر الذي تم تعديله ---
    # الآن يستخدم العرض المخصص الذي يرجع بيانات المستخدم مع التوكن
    path('api/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # ------------------------------------
    
    path('api/sessions/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('users.urls')),
    path('api/chat/', include('chat.urls')),
]