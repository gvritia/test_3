# Контрольная работа №3

Проект реализует задания `6.1-6.5`, `7.1`, `8.1`, `8.2` из PDF в одном приложении FastAPI.

Чтобы маршруты из разных заданий не конфликтовали между собой, они разнесены по префиксам:

- `6.1-6.2`: `/api/v1/basic-auth/...`
- `6.4-6.5`: `/api/v1/jwt-auth/...`
- `7.1`: `/api/v1/rbac/...`
- `8.1`: `/api/v1/sqlite-users/...`
- `8.2`: `/api/v1/todos/...`

Такой подход позволяет сохранить единый проект, не переопределяя одинаковые по смыслу пути `/register` и `/login` из разных заданий.

## Запуск

1. Создать и активировать виртуальное окружение.
2. Установить зависимости:

```powershell
pip install -r requirements.txt
```

3. Создать `.env` на основе `.env.example`.
4. При необходимости инициализировать БД:

```powershell
python init_db.py
```

5. Запустить приложение:

```powershell
uvicorn main:app --reload
```

## Переменные окружения

- `MODE=DEV|PROD`
- `DOCS_USER`
- `DOCS_PASSWORD`
- `SECRET_KEY`
- `JWT_EXPIRE_MINUTES`
- `DATABASE_PATH`

## Документация

- В `DEV` документация доступна по `/docs` и `/openapi.json`, но только по Basic Auth.
- В `PROD` маршруты `/docs`, `/openapi.json`, `/redoc` недоступны и возвращают `404 Not Found`.

## Примеры запросов

### 6.1-6.2 Basic Auth

Регистрация:

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/basic-auth/register" `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"user1\",\"password\":\"correctpass1\"}"
```

Логин:

```powershell
curl -u user1:correctpass1 "http://127.0.0.1:8000/api/v1/basic-auth/login"
```

### 6.4-6.5 JWT

Регистрация:

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/jwt-auth/register" `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}"
```

Логин:

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/jwt-auth/login" `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}"
```

Защищенный ресурс:

```powershell
curl "http://127.0.0.1:8000/api/v1/jwt-auth/protected-resource" `
  -H "Authorization: Bearer <TOKEN>"
```

### 7.1 RBAC

Регистрация пользователя с ролью:

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/rbac/register" `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"manager1\",\"password\":\"password123\",\"role\":\"user\"}"
```

### 8.1 SQLite users

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/sqlite-users/register" `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"test_user\",\"password\":\"12345\"}"
```

### 8.2 Todos

Создание:

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/todos" `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread\"}"
```

Получение:

```powershell
curl "http://127.0.0.1:8000/api/v1/todos/1"
```

Обновление:

```powershell
curl -X PUT "http://127.0.0.1:8000/api/v1/todos/1" `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread\",\"completed\":true}"
```

Удаление:

```powershell
curl -X DELETE "http://127.0.0.1:8000/api/v1/todos/1"
```
