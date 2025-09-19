from django.db import models
from django.conf import settings


class Task(models.Model):
    """
    Модель задачи, связанной с исполнителем и (опционально) с родительской задачей.
    """

    class Status(models.TextChoices):
        NEW = "new", "Не начата"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Завершена"

    title = models.CharField(
        max_length=255,
        verbose_name="Название задачи",
        help_text="Краткое название задачи",
    )

    description = models.TextField(
        blank=True,  # разрешает оставить поле пустым в формах
        verbose_name="Описание",
        help_text="Подробности задачи (необязательно)",
    )

    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,  # разрешает NULL в базе данных
        blank=True,
        related_name="tasks",
        verbose_name="Исполнитель",
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
        verbose_name="Создатель задачи",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subtasks",
        verbose_name="Родительская задача",
    )

    due_date = models.DateField(
        verbose_name="Срок выполнения",
        help_text="Дата, до которой задача должна быть завершена",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус задачи",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["created_at"]

    def __str__(self):
        """Строковое представление задачи"""
        return f"{self.title} ({self.get_status_display()})"
