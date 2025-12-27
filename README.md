# Final Task – FastAPI Microservices with Docker

Учебный проект по дисциплине «Разработка информационных систем».

Проект состоит из **двух независимых микросервисов**, реализованных на FastAPI, использующих SQLite для хранения данных и упакованных в Docker-контейнеры с использованием именованных Docker-томов.

---

## Описание сервисов

### ToDo-сервис

REST API для управления списком задач (CRUD).

Возможности:

* создание задачи
* получение списка всех задач
* получение задачи по ID
* обновление задачи
* удаление задачи

Данные хранятся в SQLite базе данных, расположенной в директории `/app/data`, подключаемой как Docker-том.

---

### Short URL сервис

Сервис для сокращения URL-адресов.

Возможности:

* создание короткой ссылки для длинного URL
* перенаправление по короткому идентификатору
* получение информации о сокращённой ссылке

Данные о ссылках хранятся в SQLite базе данных в директории `/app/data`.

---

## Структура проекта

```
final-task-isd/
├── todo_app/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── .dockerignore
├── shorturl_app/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── .dockerignore
└── README.md
```

---

## API Endpoints

### ToDo-сервис

* `POST /items` — создать задачу
* `GET /items` — получить список всех задач
* `GET /items/{item_id}` — получить задачу по ID
* `PUT /items/{item_id}` — обновить задачу
* `DELETE /items/{item_id}` — удалить задачу

### Short URL сервис

* `POST /shorten` — создать короткую ссылку
* `GET /{short_id}` — редирект на оригинальный URL
* `GET /stats/{short_id}` — получить информацию о ссылке

---

## Документация API

Каждый сервис предоставляет автоматическую документацию Swagger:

* ToDo-сервис: `http://localhost:8000/docs`
* Short URL сервис: `http://localhost:8001/docs`

---

## Запуск с использованием Docker

### 1. Создание именованных томов

```bash
docker volume create todo_data
docker volume create shorturl_data
```

### 2. Сборка Docker-образов

```bash
docker build -t baraboshkina/final-task-isd:todo ./todo_app
docker build -t baraboshkina/final-task-isd:shorturl ./shorturl_app
```

### 3. Запуск контейнеров

> ToDo-сервис использует порт 8000 внутри контейнера, Short URL сервис — порт 80.

```bash
docker run -d -p 8000:8000 -v todo_data:/app/data baraboshkina/final-task-isd:todo
docker run -d -p 8001:80 -v shorturl_data:/app/data baraboshkina/final-task-isd:shorturl
```

---

## Проверка работоспособности

### ToDo-сервис

* создать задачу: `POST /items`
* получить список задач: `GET /items`
* перезапустить контейнер и убедиться, что данные сохранены

### Short URL сервис

* создать короткую ссылку: `POST /shorten`
* перейти по короткой ссылке: `GET /{short_id}`
* получить статистику: `GET /stats/{short_id}`
* перезапустить контейнер и убедиться, что данные сохранены

---

## Используемые технологии

* Python 3.11
* FastAPI
* SQLite
* Docker / Docker Desktop (WSL2)


---

## API

### ToDo-сервис

Базовый URL: `http://localhost:8000`

Сервис реализует CRUD-операции для списка задач.  
Данные хранятся в SQLite и сохраняются между перезапусками контейнера.

#### Эндпоинты

- `POST /items`  
  Создание новой задачи.

  Тело запроса:
  ```json
  {
    "title": "string",
    "description": "string (optional)",
    "completed": false
  }
- `GET /items`
  Получение списка всех задач.

- `GET /items/{item_id}`
Получение задачи по идентификатору.

- `PUT /items/{item_id}`
Обновление задачи.
Можно передавать только изменяемые поля.

- `DELETE /items/{item_id}`
Удаление задачи.

---

### Short URL сервис
Базовый URL: `http://localhost:8001`

Сервис предназначен для сокращения URL-адресов и хранения информации о них в SQLite.

#### Эндпоинты
- `POST /shorten`
Создание короткой ссылки.

  Тело запроса:
  ```json
  {
    "url": "https://example.com"
  }
Ответ содержит короткий идентификатор и сокращённый URL.

- `GET /{short_id}`
Перенаправление на исходный URL по короткому идентификатору.

- `GET /stats/{short_id}`
Получение информации о сокращённой ссылке (оригинальный URL и время создания).

---

### Документация API
Каждый сервис предоставляет автоматическую интерактивную документацию Swagger UI:

- `/docs`
- `/redoc`

---


## Примечание

Проект предназначен для учебных целей.
