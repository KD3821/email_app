import os
from datetime import datetime

import jwt
import requests

from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import User, OAuthAccessToken, OAuthRefreshToken


AUTH_URL = os.getenv('AUTH_HOST')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
JWT_SECRET = os.getenv('JWT_SECRET')


def validate_oauth_response(response):
    if response.status_code != requests.codes.ok:
        return HttpResponseForbidden("OAuth Not Allowed")


def check_oauth_password(request_data):
    response = requests.post(
        url=f'{AUTH_URL}/tokens/',
        json={
            'username': request_data.get('email'),
            'password': request_data.get('password'),
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    )
    return response


def create_oauth_tokens(response):
    auth_data = response.json()

    if auth_data is not None:
        refresh = auth_data.get('refresh_token')
        access = auth_data.get('access_token')
        access_payload = jwt.decode(access, JWT_SECRET, algorithms=["HS256"])

        tz = timezone.get_current_timezone()
        expires_at = timezone.make_aware(datetime.fromtimestamp(access_payload.get('exp')), tz)

        try:
            user = User.objects.filter(email=access_payload.get('user').get('email'))[0:1].get()
            access_token = OAuthAccessToken.objects.create(
                user=user,
                token=access,
                expires_at=expires_at,
                scope=auth_data.get('scope'),
            )
            r_token = OAuthRefreshToken.objects.filter(user=user, revoked=False).last()  # need keep default ordering
            if refresh is not None:
                OAuthRefreshToken.objects.create(
                    user=user,
                    token=refresh,
                    access_token=access_token,
                    revoked=False
                )
                if r_token is not None:
                    r_token.revoked = True
                    r_token.save()
            else:
                r_token.access_token = access_token
                r_token.save()

        except User.DoesNotExist:
            return HttpResponseForbidden("Invalid User Credentials")


def refresh_oauth_access_token(token: OAuthRefreshToken):
    response = requests.post(
        url=f'{AUTH_URL}/refresh/',
        json={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'token': token.token
        }
    )
    validate_oauth_response(response)
    create_oauth_tokens(response)
    return response


def introspect_token(token: OAuthAccessToken | OAuthRefreshToken):
    response = requests.post(
        url=f'{AUTH_URL}/introspect/',
        json={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'token': token.token
        }
    )
    validate_oauth_response(response)
    introspect_data = response.json()
    data = {
        'refresh': introspect_data.get('refresh'),
        'active': introspect_data.get('active'),
        'revoke': introspect_data.get('revoke')
    }
    return data
