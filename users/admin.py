from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Кастомный класс для администрирования пользователей
    """

    model = CustomUser
    # Настройка отображения списка пользователей
    list_display = ("email", "full_name", "position", "is_staff")
    # Поля для фильтрации списка пользователей
    list_filter = ("is_staff", "is_superuser")
    # Поля для поиска пользователей
    search_fields = ("email", "full_name", "position")
    # Сортировка пользователей (по email по умолчанию)
    ordering = ("email",)
    # Настройка отображения формы редактирования пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личная информация", {"fields": ("full_name", "position")}),
        (
            "Права доступ",
            {
                "fields": (
                    "is_active",  # Активен ли аккаунт
                    "is_staff",  # Доступ в админ-панель
                    "is_superuser",  # Суперпользователь
                    "groups",  # Группы пользователей
                    "user_permissions",  # Индивидуальные разрешения
                ),
            },
        ),
    )
    # Настройка формы добавления нового пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),  # CSS-класс для широкой формы
                "fields": (
                    "email",  # Электронная почта
                    "full_name",  # Полное имя
                    "position",  # Должность
                    "password1",  # Пароль
                    "password2",  # Подтверждение пароля
                ),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
