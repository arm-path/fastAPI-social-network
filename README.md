## Пример Социальной сети на FastAPI
- Регистрация и авторизация пользователей.
- Профили пользователей. Добавление и удаление друзей.
- Добавление и отображение постов.
- Сообщения и чаты с использованием Websocket.

Технологии: 
- Аутентификация пользователей (JWT).
- Работа с изображениями.
- Websockets.
- Templates.

### Начало работы:
#### 1. Добавить файл ".env" со следущим содержимым:
DB_HOST='your db host' \
DB_PORT='your db port' \
DB_USER='your db user' \
DB_PASSWORD='your db password' \
DB_NAME='your db name'

JWT_USER_SECRET=your secret for jwt token

#### 2. Установить зависимости:
> pip install -r requirements.txt
### 3. Применить миграции:
> alembic revision --autogenerate \
> alembic upgrade head
#### 5. Запустить сервер FastApi:
> uvicorn src.main:app --reload

### Инструкции:
Открыть `http://localhost:8000/docs` для просмотра доступных эндпоинтов. \
Для правильной работы websocket использовать localhost http://localhost:8000/