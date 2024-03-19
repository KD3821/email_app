from typing import Optional

from rest_framework import HTTP_HEADER_ENCODING, authentication, exceptions, status
from rest_framework.request import Request

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
from django.utils import timezone

from .models import OAuthAccessToken


User = get_user_model()
AUTH_HEADER_TYPE = "Bearer"
AUTH_HEADER_TYPE_BYTES = AUTH_HEADER_TYPE.encode(HTTP_HEADER_ENCODING)


class InvalidTokenException(exceptions.AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Token is invalid or expired")
    default_code = "token_not_valid"

    def __init__(self, detail, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {'detail': force_str(detail)}
        else:
            self.detail = {'detail': force_str(self.default_detail)}


class CustomAuthentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    www_authenticate_realm = "api"
    media_type = "application/json"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user_model = User

    def authenticate(self, request: Request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token

    def authenticate_header(self, request: Request) -> str:
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPE,
            self.www_authenticate_realm,
        )

    def get_header(self, request: Request) -> bytes:
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get("HTTP_AUTHORIZATION")

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header: bytes) -> Optional[bytes]:
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] != AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise exceptions.AuthenticationFailed(
                _("Authorization header must contain two space-delimited values"),
                code="bad_authorization_header",
            )

        return parts[1]

    def get_validated_token(self, raw_token: bytes) -> OAuthAccessToken:
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        token = raw_token.decode()
        try:
            access_token = OAuthAccessToken.objects.filter(token=token, expires_at__gt=timezone.now())[0:1].get()
            return access_token
        except OAuthAccessToken.DoesNotExist:
            messages.append(
                {
                    "token_class": 'OAuthAccessToken',
                    "token_type": 'access',
                    "message": 'Token not found',
                }
            )

        raise InvalidTokenException(
            {
                "detail": _("Given token not valid for any token type"),
                "messages": messages,
            }
        )

    def get_user(self, validated_token: OAuthAccessToken) -> User | AbstractBaseUser:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user = validated_token.user
        except KeyError:
            raise InvalidTokenException(_("Token contained no recognizable user identification"))

        try:
            user = self.user_model.objects.get(**{'id': user.id})
        except self.user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("User not found"))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_("User is inactive"))

        return user
