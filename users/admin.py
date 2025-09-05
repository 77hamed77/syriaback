# users/admin.py
from django.contrib import admin
from .models import CustomUser, UserSettings

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'date_joined', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'language')