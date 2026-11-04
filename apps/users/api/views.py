from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.api.serializers import LoginRequestSerializer
from apps.users.application.services import AuthenticationService
from apps.users.infrastructure.repositories import DjangoUserRepository


class LoginView(APIView):
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "message": "Debe enviar usuario y contraseña"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AuthenticationService(user_repository=DjangoUserRepository())
        user = service.authenticate(**serializer.validated_data)
        if user is None:
            return Response(
                {"status": "error", "message": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "status": "success",
                "user": {"id": user.id, "username": user.username, "role": user.role},
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
