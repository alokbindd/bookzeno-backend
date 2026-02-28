from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


# Register your models here.
admin.site.unregister(User)
admin.site.register(UserProfile)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
