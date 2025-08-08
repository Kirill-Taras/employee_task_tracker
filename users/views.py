from rest_framework import viewsets, generics, permissions

from .models import CustomUser
from .serializers import CustomUserSerializer, UserRegisterSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления сотрудниками (пользователями).
    Поддерживает операции:
    - GET (список и отдельный пользователь)
    - POST (создание)
    - PUT/PATCH (обновление)
    - DELETE (удаление)
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserRegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
