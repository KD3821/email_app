from rest_framework import status, serializers
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission

from django.contrib.auth.models import AnonymousUser
from django.utils.encoding import force_str
from django.utils import timezone

from .models import OAuthRefreshToken, OAuthAccessToken
from .oauth import introspect_token
from .tasks import rotate_access_token


class AnonymousUserValidationError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = 'Ooops! Server error...'

    def __init__(self, detail, field, status_code):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_str(detail)}
        else:
            self.detail = {'detail': force_str(self.default_detail)}


class OAuthPermission(BasePermission):
    message = 'OAuth credentials are not provided. Please Sign-In with OAuth'

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            raise AnonymousUserValidationError(
                "Access Denied. Sign-In required.", "AccessToken", status_code=status.HTTP_403_FORBIDDEN
            )

        now = timezone.now()

        try:
            token = OAuthRefreshToken.objects.filter(user=request.user, revoked=False)[0:1].get()

            if token.access_token.expires_at > now:
                token = token.access_token

        except OAuthRefreshToken.DoesNotExist:
            raise serializers.ValidationError({'detail': self.message})

        data = introspect_token(token)

        if data.get('error'):
            self.message = data.get('error')

        if data.get('refresh'):
            if isinstance(token, OAuthAccessToken):
                token_id = token.refresh.first().pk
            else:
                token_id = token.pk

            rotate_access_token.delay(token_id)

        if data.get('revoke'):
            if isinstance(token, OAuthRefreshToken):
                token_to_revoke = token
            else:
                token_to_revoke = token.refresh.first()

            if not token_to_revoke.revoked:
                token_to_revoke.revoked = True
                token_to_revoke.save()

        return data.get('active')
