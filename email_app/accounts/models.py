from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db.models import EmailField, BooleanField, DateTimeField, CharField, ForeignKey
from django.contrib.auth.hashers import make_password, identify_hasher
from django.utils import timezone
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password, is_active=True, is_staff=False):
        if not email:
            raise ValueError('Укажите email')
        if not username:
            raise ValueError('Укажите имя')
        if not password:
            raise ValueError('Задайте пароль')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.is_active = is_active
        user.is_staff = is_staff
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        if password is None:
            raise ValueError('Задайте пароль!')
        user = self.create_user(email, username, password=password, is_staff=True)
        return user


class User(AbstractBaseUser):
    email = EmailField(max_length=255, unique=True)
    username = CharField(max_length=255)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def get_username(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        try:
            _alg = identify_hasher(self.password)
        except ValueError:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class OAuthAccessToken(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE, verbose_name='Для пользователя')
    token = CharField(max_length=300, verbose_name='OAuth Access')
    expires_at = DateTimeField(verbose_name='Годен до')
    scope = CharField(max_length=100, verbose_name='Scope')

    class Meta:
        verbose_name = 'OAuth Access Токен'
        verbose_name_plural = 'OAuth Access Токены'


class OAuthRefreshToken(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE, verbose_name='Для пользователя')
    token = CharField(max_length=300, verbose_name='OAuth Refresh')
    access_token = ForeignKey(OAuthAccessToken, on_delete=models.CASCADE, verbose_name='Access', related_name='refresh')
    revoked = BooleanField(default=False)

    class Meta:
        verbose_name = 'OAuth Refresh Токен'
        verbose_name_plural = 'OAuth Refresh Токены'
