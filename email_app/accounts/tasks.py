from celery import shared_task

from .models import OAuthRefreshToken
from .oauth import (
    refresh_oauth_access_token,
    revoke_oauth_refresh_token,
)


@shared_task
def rotate_access_token(token_id):
    r_token = OAuthRefreshToken.objects.get(id=token_id)
    result = refresh_oauth_access_token(r_token)
    return result.json()


@shared_task
def revoke_refresh_token(token_id):
    r_token = OAuthRefreshToken.objects.get(id=token_id)
    result = revoke_oauth_refresh_token(r_token)
    return result.json()


"""
export DJANGO_SETTINGS_MODULE=email_app.settings
python -m celery -A email_app worker -l info
"""