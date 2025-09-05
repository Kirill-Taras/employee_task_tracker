#!/bin/bash

set -e  # если какая-то команда падает — останавливаем скрипт

echo "📂 Копируем docker-compose.yml на сервер..."
scp docker-compose.yml $SSH_USER@$SSH_HOST:/home/$SSH_USER/employee_task_tracker/

echo "🛑 Останавливаем старые контейнеры..."
ssh $SSH_USER@$SSH_HOST "cd /home/$SSH_USER/employee_task_tracker && docker-compose down"

echo "🐳 Подтягиваем свежий образ из Docker Hub..."
ssh $SSH_USER@$SSH_HOST "cd /home/$SSH_USER/employee_task_tracker && docker-compose pull"

echo "🚀 Поднимаем контейнеры в фоне..."
ssh $SSH_USER@$SSH_HOST "cd /home/$SSH_USER/employee_task_tracker && docker-compose up -d"

echo "✅ Деплой завершён!"
