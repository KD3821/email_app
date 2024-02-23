import os
import json

from django.http import HttpResponseForbidden

from .oauth import (
    check_oauth_password,
    valid_oauth_response,
    create_oauth_tokens,
)


class RequestOAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path == os.getenv('AUTH_LOGIN_URL'):
            try:
                req_body_dict = json.loads(request.body)

                if 'email' and 'password' in req_body_dict.keys():

                    r = check_oauth_password(req_body_dict)

                    if not valid_oauth_response(r):
                        return HttpResponseForbidden("OAuth Not Allowed")

                    create_oauth_tokens(r)

            except json.decoder.JSONDecodeError:
                pass

        response = self.get_response(request)

        return response
