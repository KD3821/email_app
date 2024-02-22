import json

from .oauth import (
    check_oauth_password,
    validate_oauth_response,
    create_oauth_tokens,
)


class RequestOAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            try:
                req_body_dict = json.loads(request.body)

                if 'email' and 'password' in req_body_dict.keys():
                    r = check_oauth_password(req_body_dict)

                    validate_oauth_response(r)

                    create_oauth_tokens(r)

            except json.decoder.JSONDecodeError:
                pass

        response = self.get_response(request)

        return response
