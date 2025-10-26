#!/bin/bash
set -e

echo "========================================="
echo "Deltica Backend - Starting..."
echo "========================================="

# Ожидание готовности PostgreSQL
echo "[1/4] Waiting for PostgreSQL to be ready..."
until pg_isready -h $DB_HOST -U $DB_USER -d $DB_NAME; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is ready!"

# Применение миграций Alembic
echo "[2/4] Applying database migrations..."
uv run alembic upgrade head
echo "Migrations applied successfully!"

# Создание начальных пользователей
echo "[3/4] Seeding initial users..."
uv run python backend/scripts/seed_users.py || {
  echo "Warning: User seeding failed (this is normal if users already exist)"
}
echo "User seeding completed!"

# Запуск FastAPI приложения
echo "[4/4] Starting FastAPI backend..."
echo "========================================="
echo "Backend is running on http://0.0.0.0:8000"
echo "API docs available at http://0.0.0.0:8000/docs"
echo "========================================="

exec uv run uvicorn backend.core.main:app --host 0.0.0.0 --port 8000
