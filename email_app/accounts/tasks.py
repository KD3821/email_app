from celery import shared_task

from .models import OAuthRefreshToken
from .oauth import refresh_oauth_access_token


@shared_task
def rotate_refresh_token(token_id):
    r_token = OAuthRefreshToken.objects.get(id=token_id)
    refresh_oauth_access_token(r_token)
