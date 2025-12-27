# ToDo и URL Shortener

Два микросервиса на FastAPI с SQLite базами данных, упакованные в Docker контейнеры.

### ToDo-сервис
API для управления списком задач. Каждая задача имеет:
- `id` - уникальный идентификатор
- `title` - название задачи
- `description` - описание (опционально)
- `completed` - статус выполнения

### URL Shortener сервис
Сервис для сокращения URL-адресов. Создает короткие ссылки и обеспечивает редирект на оригинальные URL.

## Локальный запуск

### ToDo-сервис

```bash
cd todo_app

python -m venv .venv
source .venv/bin/activate  

pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервис будет доступен по адресу: http://localhost:8000

### URL Shortener 

```bash
cd shorturl_app

python -m venv .venv
source venv/bin/activate 

pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Сервис будет доступен по адресу: http://localhost:8001

## Запуск с Docker

### Шаг 1: Создание именованных томов

```bash
docker volume create todo_data
docker volume create shorturl_data
```

### Шаг 2: Сборка Docker образов

```bash
docker build -t todo-service ./todo_app
docker build -t shorturl-service ./shorturl_app
```

### Шаг 3: Запуск контейнеров

```bash
docker run -d -p 8000:80 -v todo_data:/app/data --name todo-app todo-service
docker run -d -p 8001:80 -v shorturl_data:/app/data --name shorturl-app shorturl-service
```

## API документация

После запуска сервисов автоматическая интерактивная документация доступна по адресам:

- ToDo сервис: http://localhost:8000/docs
- URL Shortener сервис: http://localhost:8001/docs

## Примеры использования

### ToDo-сервис

#### Создание задачи
```bash
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Купить молоко",
    "description": "В магазине на углу",
    "completed": false
  }'
```

Ответ:
```json
{
  "id": 1,
  "title": "Купить молоко",
  "description": "В магазине на углу",
  "completed": false
}
```

#### Получение всех задач
```bash
curl http://localhost:8000/items
```

#### Получение задачи по ID
```bash
curl http://localhost:8000/items/1
```

#### Обновление задачи
```bash
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

#### Удаление задачи
```bash
curl -X DELETE http://localhost:8000/items/1
```

### URL Shortener сервис

#### Создание короткой ссылки
```bash
curl -X POST "http://localhost:8001/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com/very/long/url"
  }'
```

Ответ:
```json
{
  "short_id": "aB3xY9",
  "short_url": "/aB3xY9",
  "full_url": "https://www.example.com/very/long/url"
}
```

#### Редирект по короткой ссылке
```bash
curl -L http://localhost:8001/aB3xY9
```

#### Получение информации о ссылке
```bash
curl http://localhost:8001/stats/aB3xY9
```

Ответ:
```json
{
  "short_id": "aB3xY9",
  "full_url": "https://www.example.com/very/long/url",
  "created_at": "2025-12-23T10:30:45.123456"
}
```