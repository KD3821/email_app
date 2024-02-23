from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .renderers import UserRenderer
from .utils import revoke_oauth_access
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
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


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        revoke_oauth_access(request.user.email)
        return Response(status=status.HTTP_204_NO_CONTENT)