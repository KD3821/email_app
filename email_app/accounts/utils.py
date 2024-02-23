from .models import OAuthRefreshToken
from .tasks import revoke_refresh_token


def revoke_oauth_access(email):
    try:
        oauth_refresh_token = OAuthRefreshToken.objects.filter(user__email=email, revoked=False)[0:1].get()
        revoke_refresh_token.delay(oauth_refresh_token.pk)
        oauth_refresh_token.revoked = True
        oauth_refresh_token.save()
    except OAuthRefreshToken.DoesNotExist:
        pass
