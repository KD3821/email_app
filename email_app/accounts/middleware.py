import os
import json

from django.http import HttpResponseForbidden, HttpResponseBadRequest

from .oauth import (
    check_oauth_password,
    valid_oauth_response,
    create_oauth_tokens,
)


class RequestOAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path == os.getenv('AUTH_LOGIN_URL') and request.method == 'POST' and response.status_code == 200:
            try:
                req_body_dict = json.loads(request.body)

                if 'email' and 'password' in req_body_dict.keys():

                    r = check_oauth_password(req_body_dict)

                    if not valid_oauth_response(r):
                        if r.status_code == 500:
                            return HttpResponseBadRequest('Сервис не доступен. Мы работаем, чтобы это исправить.')
                        return HttpResponseForbidden('Доступ к сервису ограничен - обратитесь в поддержку.')

                    create_oauth_tokens(r)

            except json.decoder.JSONDecodeError:
                pass

        return response
