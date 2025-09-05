from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date, timedelta

from users.models import CustomUser
from .models import Task


class TaskAPITests(TestCase):
    """
    Набор тестов для проверки API задач:
    - Создание, чтение, обновление и удаление задач
    - Проверка прав доступа
    - Кастомные эндпоинты (busy-employees, important-tasks)
    - Валидация данных
    """

    def setUp(self):
        """
        Подготовка тестовых данных.
        Создаем тестовых пользователей и задачи.
        """
        self.client = APIClient()

        # Создаем тестовых пользователей
        self.manager = CustomUser.objects.create_user(
            email="manager@example.com",
            password="managerpass",
            full_name="Manager User",
            position="Manager",
        )

        self.employee1 = CustomUser.objects.create_user(
            email="employee1@example.com",
            password="emppass1",
            full_name="Employee One",
            position="Developer",
        )

        self.employee2 = CustomUser.objects.create_user(
            email="employee2@example.com",
            password="emppass2",
            full_name="Employee Two",
            position="Tester",
        )

        # Создаем тестовые задачи
        self.task1 = Task.objects.create(
            title="Разработать API",
            description="Создать REST API для системы",
            due_date=date.today() + timedelta(days=7),
            status=Task.Status.IN_PROGRESS,
            creator=self.manager,
            executor=self.employee1,
        )

        self.task2 = Task.objects.create(
            title="Написать тесты",
            description="Покрыть код unit-тестами",
            due_date=date.today() + timedelta(days=5),
            status=Task.Status.NEW,
            creator=self.manager,
            executor=self.employee2,
        )

        # Задача без исполнителя
        self.task3 = Task.objects.create(
            title="Документирование",
            description="Подготовить документацию",
            due_date=date.today() + timedelta(days=10),
            status=Task.Status.NEW,
            creator=self.manager,
        )

        # URL для работы с задачами
        self.list_url = reverse("tasks-list")
        self.detail_url = lambda pk: reverse("tasks-detail", kwargs={"pk": pk})
        self.busy_employees_url = reverse("tasks-busy-employees")
        self.important_tasks_url = reverse("tasks-important-tasks")

    def test_get_tasks_requires_auth(self):
        """
        Проверяем, что список задач доступен только авторизованным пользователям.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task(self):
        """
        Тестируем создание новой задачи авторизованным пользователем.
        """
        self.client.force_authenticate(user=self.manager)

        data = {
            "title": "Новая задача",
            "description": "Описание новой задачи",
            "due_date": date.today() + timedelta(days=14),
            "status": Task.Status.NEW,
            "executor_id": self.employee1.id,
        }

        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что задача создалась с правильным создателем
        task = Task.objects.get(id=response.data["id"])
        self.assertEqual(task.creator, self.manager)
        self.assertEqual(task.executor, self.employee1)

    def test_update_task(self):
        """
        Тестируем обновление задачи.
        """
        self.client.force_authenticate(user=self.manager)

        updated_data = {
            "title": "Обновленное название",
            "status": Task.Status.IN_PROGRESS,
            "executor_id": self.employee2.id,
        }

        response = self.client.patch(
            self.detail_url(self.task1.id), updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Обновляем объект из базы
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Обновленное название")
        self.assertEqual(self.task1.status, Task.Status.IN_PROGRESS)
        self.assertEqual(self.task1.executor, self.employee2)

    def test_delete_task(self):
        """
        Тестируем удаление задачи.
        """
        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(self.detail_url(self.task1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_busy_employees_endpoint(self):
        """
        Тестируем кастомный эндпоинт busy-employees.
        Должен возвращать список сотрудников с количеством активных задач.
        """
        self.client.force_authenticate(user=self.manager)

        response = self.client.get(self.busy_employees_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа
        self.assertTrue(isinstance(response.data, list))
        self.assertGreater(len(response.data), 0)

        # Проверяем, что employee1 имеет 1 активную задачу
        emp1_data = next(
            (
                item
                for item in response.data
                if item["employee"]["email"] == "employee1@example.com"
            ),
            None,
        )
        self.assertIsNotNone(emp1_data)
        self.assertEqual(emp1_data["active_tasks_count"], 1)

    def test_important_tasks_endpoint(self):
        """
        Тестируем кастомный эндпоинт important-tasks.
        Должен возвращать задачи без исполнителя, от которых зависят другие задачи.
        """
        # Создаем подзадачу для task3 (которая без исполнителя)
        subtask = Task.objects.create(
            title="Подзадача для документирования",
            description="Часть документации",
            due_date=date.today() + timedelta(days=8),
            status=Task.Status.IN_PROGRESS,
            creator=self.manager,
            executor=self.employee1,
            parent=self.task3,
        )
        self.assertTrue(Task.objects.filter(parent=self.task3).exists())
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.important_tasks_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertGreater(len(response.data), 0)
        # Проверяем, что task3 попала в важные задачи
        task_data = next(
            (item for item in response.data if item["task"] == "Документирование"), None
        )
        self.assertIsNotNone(task_data)

        # Проверяем, что в предложенных исполнителях есть employee1 (исполнитель подзадачи)
        self.assertIn(self.employee1.full_name, task_data["available_employees"])

    def test_task_validation(self):
        """
        Тестируем валидацию данных при создании/обновлении задачи.
        """
        self.client.force_authenticate(user=self.manager)

        # Пытаемся создать задачу с прошедшей датой
        invalid_data = {
            "title": "Невалидная задача",
            "due_date": date.today() - timedelta(days=1),
            "status": Task.Status.NEW,
        }

        response = self.client.post(self.list_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data)
