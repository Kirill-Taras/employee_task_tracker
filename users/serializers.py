from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CustomUser."""

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'full_name',
            'position',
            'phone',
            'avatar',
            'is_active',
            'password',
        ]
        extra_kwargs = {'is_active': {'read_only': True}}

    def create(self, validated_data):
        """
        Переопределяем метод create, чтобы пароль хэшировался.
        """
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # хэшируем пароль
        user.save()
        return user


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя с паролем."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'full_name',
            'position',
            'phone',
            'avatar',
            'password',
        ]

    def create(self, validated_data):
        # Пароль нужно хэшировать через set_password
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user