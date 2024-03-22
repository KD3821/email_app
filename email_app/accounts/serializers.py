from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.contrib import auth

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError({
                'username': ['Имя пользователя может содержать только цифры и буквы (без пробелов)']
            })
        if email.index('@') == -1 and email.index('.') == -1:
            raise serializers.ValidationError(
                {'email': ['Некорректный email']}
            )
        attrs['email'] = email.lower()
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'username',
            'tokens'
        ]

    def validate(self, attrs):
        email = attrs.get('email', '')
        email = email.lower()
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed({
                'detail': ['Неправильный логин или пароль. Попробуйте еще раз']
            })
        if not user.is_active:
            raise AuthenticationFailed({
                'detail': ['Аккаунт не активен, свяжитесь с поддержкой.']
            })
        if not user.is_verified:
            raise AuthenticationFailed({
                'detail': ['Email еще не подтвержден.']
            })
        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens()
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {'bad_token': 'Токен не действительный'}

    def validate(self, data):
        self.token = data.get('refresh')
        return data

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')
