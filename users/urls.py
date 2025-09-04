from django.urls import path
from .views import RegisterView, UserProfileView, UserSettingsView, ChangePasswordView, DeleteAccountView, ExportUserDataView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/profile/', UserProfileView.as_view(), name='profile'),
    path('me/settings/', UserSettingsView.as_view(), name='settings'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('me/delete/', DeleteAccountView.as_view(), name='delete-account'), # مسار منفصل للحذف
    path('me/export/', ExportUserDataView.as_view(), name='export-data'),
]