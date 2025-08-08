# tasks/views.py
from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления задачами.
    Реализует CRUD-операции:
    - GET /tasks/ — список всех задач
    - GET /tasks/<id>/ — получить задачу
    - POST /tasks/ — создать новую задачу
    - PUT/PATCH /tasks/<id>/ — обновить задачу
    - DELETE /tasks/<id>/ — удалить задачу
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]  # доступ только авторизованным

    def perform_create(self, serializer):
        """
        При создании задачи автоматически проставляем автора (creator)
        из текущего авторизованного пользователя.
        """
        serializer.save(creator=self.request.user)
