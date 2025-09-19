# Employee Task Tracker

## 📖 Описание проекта
**Employee Task Tracker** — это веб-сервис для управления задачами сотрудников.  
Проект позволяет:
- Создавать и управлять сотрудниками.
- Создавать и назначать задачи.
- Следить за загрузкой сотрудников.

Приложение реализовано на **Django + Django REST Framework** с использованием **PostgreSQL**.  
API документировано через **Swagger (drf-yasg)**.

---

## ⚙️ Стек технологий
- Python 
- Django 
- Django REST Framework
- PostgreSQL
- drf-yasg (Swagger документация)
- JWT (аутентификация)

---

## 🚀 Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Kirill-Taras/employee_task_tracker.git
cd employee_task_tracker
```

### 2. Создать виртуальное окружение и активировать его
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
.venv\Scripts\activate     # для Windows
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить .env файл
```bash
DB_NAME=task_tracker
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_secret_key
```

### 5. Применить миграции
```bash
python manage.py migrate
```

### 6. Создать суперпользователя
```bash
python manage.py createsuperuser
```

### 7. Запустить сервер
```bash
python manage.py runserver
```

📌 API
После запуска проекта доступна автодокументация:

Swagger UI → http://127.0.0.1:8000/swagger/

ReDoc → http://127.0.0.1:8000/redoc/

🔑 Аутентификация

Используется JWT:

POST /api/token/ — получить токен

POST /api/token/refresh/ — обновить токен

👤 Пользователи

POST /api/register/ — регистрация

GET /api/users/ — список пользователей (только для авторизованных)

GET /api/users/{id}/ — получить данные пользователя

PUT/PATCH /api/users/{id}/ — обновить пользователя

DELETE /api/users/{id}/ — удалить пользователя

✅ Задачи

GET /api/tasks/ — список задач

POST /api/tasks/ — создать задачу

GET /api/tasks/{id}/ — получить задачу

PUT/PATCH /api/tasks/{id}/ — обновить задачу

DELETE /api/tasks/{id}/ — удалить задачу

⭐ Специальные эндпоинты

GET /api/tasks/busy-employees/ — список сотрудников с количеством активных задач

GET /api/tasks/important-tasks/ — список важных задач и кандидатов на исполнение