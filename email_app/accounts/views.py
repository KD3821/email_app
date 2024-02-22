from rest_framework import status, generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import User
from .serializers import RegisterSerializer, LoginSerializer
from .renderers import UserRenderer


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
        # print(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
