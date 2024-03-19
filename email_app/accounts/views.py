from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .renderers import UserRenderer
from .models import OAuthRefreshToken
from .utils import revoke_oauth_access
from .oauth import valid_oauth_response, refresh_oauth_access_token
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
)


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        return Response(user_data, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout(request):
    email = request.data.get('email')
    refresh = request.data.get('refresh')
    revoke_oauth_access(email, refresh)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def token_refresh(request):
    data = request.data
    refresh = data.get('refresh')
    try:
        refresh_token = OAuthRefreshToken.objects.filter(token=refresh, revoked=False)[0:1].get()
        response = refresh_oauth_access_token(refresh_token)
        if valid_oauth_response(response):
            response_data = response.json()
            return Response(
                {'access': response_data.get('access_token')},
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Необходимо повторно авторизоваться'},
            status=status.HTTP_403_FORBIDDEN
        )
    except OAuthRefreshToken.DoesNotExist:
        return Response(status=status.HTTP_403_FORBIDDEN)
