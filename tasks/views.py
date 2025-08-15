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
                    filter=Q(
                        tasks__status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS]
                    ),
                )
            )
            .filter(active_tasks_count__gt=0)
            .order_by("-active_tasks_count")
        )

        # Формируем список для ответа
        data = []
        for emp in employees:
            tasks = emp.tasks.filter(
                status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS]
            )
            data.append(
                {
                    "employee": UserShortSerializer(emp).data,
                    "active_tasks_count": emp.active_tasks_count,
                    "tasks": TaskSerializer(tasks, many=True).data,
                }
            )

        return Response(data)

    @action(detail=False, methods=["get"], url_path="important-tasks")
    def important_tasks(self, request):
        """
        Эндпоинт "Важные задачи":
        - Задачи без исполнителя, но от которых зависят задачи в работе
        - Определение сотрудников, кто может их взять
        """
        candidate_tasks = Task.objects.filter(executor__isnull=True)
        candidate_tasks = candidate_tasks.filter(
            subtasks__status__in=[Task.Status.IN_PROGRESS, Task.Status.DONE]
        ).distinct()

        employees_with_load = CustomUser.objects.annotate(
            active_tasks_count=Count(
                "tasks",
                filter=Q(tasks__status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS]),
            )
        )

        # Наименее загруженный
        min_load = (
            employees_with_load.aggregate(
                min_count=Count(
                    "tasks",
                    filter=Q(
                        tasks__status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS]
                    ),
                )
            )["min_count"]
            or 0
        )

        result = []
        for task in candidate_tasks:
            available_employees = []

            # Наименее загруженные сотрудники
            least_loaded = employees_with_load.filter(active_tasks_count=min_load)
            available_employees.extend([f"{u.full_name}" for u in least_loaded])

            # Сотрудник, выполняющий родительскую задачу
            if task.parent and task.parent.executor:
                parent_executor = task.parent.executor
                parent_active_tasks_count = parent_executor.tasks.filter(
                    status__in=[Task.Status.NEW, Task.Status.IN_PROGRESS]
                ).count()
                if parent_active_tasks_count <= min_load + 2:
                    available_employees.append(parent_executor.full_name)

            result.append(
                {
                    "task": task.title,
                    "due_date": task.due_date,
                    "available_employees": list(
                        set(available_employees)
                    ),  # убираем дубликаты
                }
            )

        return Response(result)
