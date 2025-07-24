from django.contrib import admin
from .models import User, AuthCode

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'invite_code', 'activated_invite_code', 'date_joined')
    search_fields = ('phone', 'invite_code')
    list_filter = ('is_active', 'is_staff')
    readonly_fields = ('date_joined', 'last_login')

@admin.register(AuthCode)
class AuthCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'code', 'created_at')
    search_fields = ('phone',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)