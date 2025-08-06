from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер пользователей: создает пользователей по email без username
    """

    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError("У пользователя должен быть email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Расширенная модель пользователя
    Добавлены поля: email, ФИО, должность, телефон, аватар.
    """

    objects = CustomUserManager()
    username = None  # Удаляем стандартное поле username

    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
        help_text="Используется для входа в систему",
    )

    full_name = models.CharField(
        max_length=255, verbose_name="ФИО", help_text="Полное имя сотрудника"
    )

    position = models.CharField(
        max_length=100,
        verbose_name="Должность",
        help_text="Роль или должность сотрудника",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
        help_text="Контактный номер телефона",
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Изображение профиля",
    )

    USERNAME_FIELD = "email"  # Указываем, что логином является email
    REQUIRED_FIELDS = ["full_name", "position"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def __str__(self):
        """
        Отображение пользователя в виде строки
        """
        return f"{self.full_name} ({self.email})"
