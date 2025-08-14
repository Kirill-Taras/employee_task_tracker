from django.db.models import Count, Q
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import CustomUser
from .models import Task
from .serializers import TaskSerializer, UserShortSerializer


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

    @action(detail=False, methods=["get"], url_path="busy-employees")
    def busy_employees(self, request):
        """
        Специальный эндпоинт: список сотрудников по загрузке.
        Возвращает сотрудников с количеством активных задач (new, in_progress),
        отсортированных по количеству задач по убыванию.
        """
        employees = (
            CustomUser.objects.annotate(
                active_tasks_count=Count(
                    "tasks",
                    filter=Q(tasks__status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS])
                )
            )
            .filter(active_tasks_count__gt=0)
            .order_by("-active_tasks_count")
        )

        # Формируем список для ответа
        data = []
        for emp in employees:
            tasks = emp.tasks.filter(status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS])
            data.append({
                "employee": UserShortSerializer(emp).data,
                "active_tasks_count": emp.active_tasks_count,
                "tasks": TaskSerializer(tasks, many=True).data
            })

        return Response(data)
