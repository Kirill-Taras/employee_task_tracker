from rest_framework import serializers
from .models import Task
from users.models import CustomUser


class UserShortSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор для краткой информации о пользователе.
    """

    class Meta:
        model = CustomUser
        fields = ["id", "email", "first_name", "last_name", "phone", "avatar"]


class TaskSerializer(serializers.ModelSerializer):
    creator = UserShortSerializer(read_only=True)
    executor = UserShortSerializer(read_only=True)

    executor_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="executor",
        write_only=True,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "creator",
            'due_date',
            "executor",
            "executor_id",
            "parent",
            "created_at",
            "updated_at",
        ]
