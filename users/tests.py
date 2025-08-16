from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import CustomUser


class UserAPITests(TestCase):
    """
    Набор тестов для проверки API пользователей.
    """

    def setUp(self):
        """
        Запускается перед каждым тестом.
        Здесь мы создаём клиента API и тестового суперпользователя.
        """
        self.client = APIClient()

        # Создаём суперпользователя (для админ-доступа, если потребуется)
        self.admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            full_name="Admin User",
            position="Admin"
        )

        # Создаём обычного пользователя
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password="userpass",
            full_name="Regular User",
            position="Employee"
        )

        # URL для регистрации пользователя
        self.register_url = reverse("users-register")  # имя маршрута в urls.py

        # URL для получения списка пользователей
        self.list_url = reverse("users-list")

    def test_register_user(self):
        """
        Тестируем регистрацию нового пользователя через API.
        """
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "full_name": "New User",
            "position": "Developer",
        }
        response = self.client.post(self.register_url, data, format="json")

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Проверяем, что пользователь создался в базе
        self.assertTrue(CustomUser.objects.filter(email="newuser@example.com").exists())

    def test_get_users_requires_auth(self):
        """
        Проверяем, что список пользователей доступен только авторизованным.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_users_authorized(self):
        """
        Проверяем, что авторизованный пользователь может получить список.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_duplicate_email_registration(self):
        """
        Проверяем, что нельзя зарегистрировать пользователя с существующим email.
        """
        data = {
            "email": "user@example.com",  # уже есть в setUp
            "password": "somepass",
            "full_name": "Duplicate User",
            "position": "Tester",
        }
        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
