import os
import jwt
import json
from datetime import datetime

import requests

from django.http import HttpResponseForbidden

from .models import User, OAuthAccessToken, OAuthRefreshToken


AUTH_URL = os.getenv('AUTH_HOST')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
JWT_SECRET = os.getenv('JWT_SECRET')


class RequestOAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_data = None

        try:
            req_body_dict = json.loads(request.body)

            if 'email' and 'password' in req_body_dict.keys():
                r = requests.post(
                    url=f'{AUTH_URL}/token/',
                    json={
                        'grant_type': 'password',
                        'username': req_body_dict.get('email'),
                        'password': req_body_dict.get('password'),
                        'client_id': CLIENT_ID,
                        'client_secret': CLIENT_SECRET
                    }
                )
                auth_data = r.json()
        except json.decoder.JSONDecodeError:
            pass

        response = self.get_response(request)

        if auth_data is not None:
            if r.status_code != requests.codes.ok:
                return HttpResponseForbidden("OAuth Not Allowed")
            refresh = auth_data.get('refresh_token')
            access = auth_data.get('access_token')
            access_payload = jwt.decode(access, JWT_SECRET, algorithms=["HS256"])
            try:
                user = User.objects.filter(email=access_payload.get('user').get('email'))[0:1].get()
                access_token = OAuthAccessToken.objects.create(
                    user=user,
                    token=access,
                    expires_at=datetime.utcfromtimestamp(access_payload.get('exp')).isoformat(),
                    scope=auth_data.get('scope'),
                )
                OAuthRefreshToken.objects.create(
                    user=user,
                    token=refresh,
                    access_token=access_token,
                    revoked=None
                )
            except User.DoesNotExist:
                pass

        return response
