FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv через pip
RUN pip install --no-cache-dir uv

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка Python зависимостей
RUN uv sync --no-dev

# Копирование кода приложения
COPY backend/ ./backend/
COPY migrations/ ./migrations/
COPY alembic.ini ./
COPY config/ ./config/

# Создание необходимых директорий
RUN mkdir -p backend/uploads backend/backups backend/logs backend/generated_documents

# Порт приложения
EXPOSE 8000

# Копирование и установка прав на entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Запуск приложения
CMD ["/entrypoint.sh"]
