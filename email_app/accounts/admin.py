from django.contrib import admin

from .models import User, OAuthAccessToken, OAuthRefreshToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'is_active', 'is_staff', 'created_at', 'is_verified']


@admin.register(OAuthAccessToken)
class OAuthAccessAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'token', 'expires_at', 'scope']


@admin.register(OAuthRefreshToken)
class OAuthAccessAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'token', 'access_token_id', 'revoked']
