API для управления задачами с аутентификацией и системой прав доступа.
Установка
# Клонировать репозиторий
git clone https://github.com/arepresstore/todo-api.git
cd todo-api

# Создать и активировать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# Установить зависимости
pip install -r requirements.txt

Настройка базы данных
Создать БД PostgreSQL

Обновить настройки в todo_api/settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'todo_db',
        'USER': 'username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
Примените миграции:

python manage.py migrate


Запуск сервера
bash
python manage.py runserver

Примеры запросов через curl
1. Регистрация пользователя
bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
Ответ:

json
{
  "id": 1,
  "username": "testuser"
}

2. Получение токена аутентификации
bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
Ответ:

json
{
  "token": "9944b09199c62b...",
  "user_id": 1,
  "username": "testuser"
}
3. Создание задачи (требуется токен)
bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Token 9944b09199c62b..." \
  -H "Content-Type: application/json" \
  -d '{"title": "Купить молоко", "description": "2.5%"}'
Ответ:

json
{
  "id": 1,
  "title": "Купить молоко",
  "description": "2.5%",
  "completed": false,
  "created_at": "2023-10-01T12:00:00Z",
  "owner": {
    "id": 1,
    "username": "testuser"
  }
}
4. Получение списка задач
bash
curl -X GET http://localhost:8000/api/tasks/ \
  -H "Authorization: Token 9944b09199c62b..."
5. Обновление задачи
bash
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Token 9944b09199c62b..." \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
6. Удаление задачи
bash
curl -X DELETE http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Token 9944b09199c62b..."

Управление правами доступа
1. Предоставление прав на задачу
bash
curl -X POST http://localhost:8000/api/tasks/1/share/ \
  -H "Authorization: Token 9944b09199c62b..." \
  -H "Content-Type: application/json" \
  -d '{"username": "otheruser", "permission": "read"}'
2. Отзыв прав на задачу
bash
curl -X DELETE http://localhost:8000/api/tasks/1/share/ \
  -H "Authorization: Token 9944b09199c62b..." \
  -H "Content-Type: application/json" \
  -d '{"username": "otheruser"}'
