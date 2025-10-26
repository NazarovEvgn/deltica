# Deltica Production Deployment Plan
# План подготовки к production развертыванию

## Архитектура

```
┌─────────────────────────────────────┐
│  СЕРВЕР (Windows Server / Linux)    │
│  ┌───────────────────────────────┐  │
│  │ Docker Compose                │  │
│  │  ├─ Backend (FastAPI)         │  │
│  │  └─ PostgreSQL 17             │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
              ↑
              │ HTTP API (локальная сеть)
              ↓
┌─────────────────────────────────────┐
│  РАБОЧИЕ ПК (100+ станций)          │
│  ┌───────────────────────────────┐  │
│  │ Deltica.exe (Electron)        │  │
│  │ - Frontend (Vue + RevoGrid)   │  │
│  │ - API: http://server:8000     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## Этап 1: Docker контейнеризация backend

### Задачи:
- [ ] Создать `Dockerfile` для backend
- [ ] Создать `docker-compose.yml` (backend + PostgreSQL + volumes)
- [ ] Создать `.env.production` с переменными окружения
- [ ] Создать `docker/entrypoint.sh` (миграции + seed)
- [ ] Протестировать сборку и запуск

### Файлы для создания:

**Dockerfile:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install uv

# Копирование зависимостей
COPY pyproject.toml uv.lock ./

# Установка Python зависимостей
RUN uv sync --no-dev

# Копирование кода
COPY . .

# Порт
EXPOSE 8000

# Entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:17-alpine
    container_name: deltica_postgres
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    container_name: deltica_backend
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      SECRET_KEY: ${SECRET_KEY}
    volumes:
      - ./backend/uploads:/app/backend/uploads
      - ./backend/backups:/app/backend/backups
      - ./backend/logs:/app/backend/logs
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
```

**.env.production:**
```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=deltica_prod
DB_USER=deltica_user
DB_PASSWORD=CHANGE_THIS_STRONG_PASSWORD

# Backend
SECRET_KEY=CHANGE_THIS_SECRET_KEY_MINIMUM_32_CHARACTERS
```

**docker/entrypoint.sh:**
```bash
#!/bin/bash
set -e

# Ожидание готовности PostgreSQL
echo "Waiting for PostgreSQL..."
while ! pg_isready -h postgres -U $DB_USER; do
  sleep 1
done

# Применение миграций
echo "Applying database migrations..."
uv run alembic upgrade head

# Создание начальных пользователей
echo "Seeding initial users..."
uv run python backend/scripts/seed_users.py || true

# Запуск backend
echo "Starting backend..."
exec uv run uvicorn backend.core.main:app --host 0.0.0.0 --port 8000
```

**Проверка:**
```bash
docker-compose up -d
curl http://localhost:8000/docs
```

---

## Этап 2: Production конфигурация Electron

### Задачи:
- [ ] Создать `frontend/.env.production`
- [ ] Создать `frontend/build/icon.ico`
- [ ] Обновить `frontend/package.json` (electron-builder config)
- [ ] Отключить DevTools в production
- [ ] Протестировать сборку установщика

### Файлы для создания:

**frontend/.env.production:**
```bash
# Production API URL - ИЗМЕНИТЬ НА ВАШ СЕРВЕР!
VITE_API_URL=http://192.168.1.100:8000

# Или доменное имя
# VITE_API_URL=http://deltica-server.local:8000
```

**frontend/package.json** (добавить в секцию "build"):
```json
{
  "build": {
    "appId": "com.gazpromneft.deltica",
    "productName": "Deltica",
    "directories": {
      "output": "dist-electron",
      "buildResources": "build"
    },
    "files": [
      "dist/**/*",
      "electron/**/*",
      "package.json"
    ],
    "win": {
      "target": "nsis",
      "icon": "build/icon.ico",
      "publisherName": "Gazprom Neft"
    },
    "nsis": {
      "oneClick": false,
      "perMachine": true,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "Deltica",
      "license": "LICENSE.txt"
    }
  }
}
```

**frontend/electron/main.js** (отключить DevTools в production):
```javascript
// В режиме разработки загружаем из Vite dev server
if (process.env.NODE_ENV === 'development') {
  // Очистка кэша в dev режиме для предотвращения проблем с RevoGrid
  mainWindow.webContents.session.clearCache()

  mainWindow.loadURL('http://localhost:5173')
  mainWindow.webContents.openDevTools()
} else {
  // В production загружаем собранные файлы
  mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  // DevTools отключены в production
}
```

**Создание иконки:**
```bash
# Конвертировать favicon.png в .ico с несколькими размерами
# Размеры: 16, 32, 48, 64, 128, 256
# Сохранить в frontend/build/icon.ico
```

**Сборка установщика:**
```bash
cd frontend

# Установка зависимостей (если нужно)
npm install

# Production сборка
npm run electron:build:win

# Результат: frontend/dist-electron/Deltica-Setup-1.0.0.exe (~150 MB)
```

---

## Этап 3: Документация развертывания

### Задачи:
- [ ] Создать `docs/DEPLOYMENT.md` - установка сервера
- [ ] Создать `docs/CLIENT_INSTALL.md` - установка клиента
- [ ] Создать `docs/UPDATE.md` - обновление системы
- [ ] Создать `docs/USER_GUIDE.md` - руководство пользователя
- [ ] Создать `docs/ADMIN_GUIDE.md` - руководство администратора

### Структура документов:

**DEPLOYMENT.md:**
- Системные требования сервера
- Установка Docker и Docker Compose
- Клонирование репозитория
- Настройка `.env.production`
- Запуск контейнеров
- Проверка работоспособности
- Настройка firewall
- Настройка автозапуска

**CLIENT_INSTALL.md:**
- Системные требования клиента
- Скачивание `Deltica-Setup-1.0.0.exe`
- Процесс установки
- Первый запуск
- Troubleshooting (типовые проблемы)

**UPDATE.md:**
- Обновление backend (пересоздание контейнера)
- Обновление клиентских установщиков
- Откат к предыдущей версии
- Backup перед обновлением

**USER_GUIDE.md:**
- Вход в систему
- Работа с оборудованием (CRUD)
- Фильтрация и поиск
- Архивирование
- Загрузка/скачивание файлов
- Генерация документов
- Статистика

**ADMIN_GUIDE.md:**
- Управление пользователями (sync_users.py)
- Создание backup
- Мониторинг системы
- Просмотр логов
- Обновление системы
- Устранение типовых проблем

---

## Этап 4: Скрипты автоматизации

### Задачи:
- [ ] Создать `deploy/install-server.sh` - установка сервера (Linux)
- [ ] Создать `deploy/backup.sh` - автоматический backup
- [ ] Создать `deploy/update-server.sh` - обновление сервера
- [ ] Создать `deploy/build-electron.ps1` - сборка Electron (Windows)

### Скрипты:

**deploy/install-server.sh:**
```bash
#!/bin/bash
# Установка Docker, Docker Compose, запуск контейнеров
# Для Ubuntu/Debian
```

**deploy/backup.sh:**
```bash
#!/bin/bash
# - pg_dump базы данных
# - Копирование uploaded файлов
# - Ротация старых backup (30 дней)
```

**deploy/update-server.sh:**
```bash
#!/bin/bash
# - Backup перед обновлением
# - Pull новых образов
# - Применение миграций
# - Перезапуск контейнеров
```

**deploy/build-electron.ps1:**
```powershell
# - npm install
# - npm run build
# - npm run electron:build:win
# - Копирование установщика в shared folder
```

---

## Этап 5: Тестирование production

### Задачи:
- [ ] Развертывание на тестовом сервере
- [ ] Установка на 3 тестовых ПК
- [ ] Проверка CRUD операций
- [ ] Проверка файлов (загрузка/скачивание)
- [ ] Проверка одновременной работы 3 пользователей
- [ ] Проверка backup/restore
- [ ] Стресс-тест (10+ пользователей, 1000+ записей)

---

## Этап 6: Усиление безопасности

### Задачи:

**Backend:**
- [ ] HTTPS (SSL/TLS сертификаты)
- [ ] Rate limiting (защита от брутфорса)
- [ ] Блокировка после 5 неудачных попыток входа
- [ ] Логирование всех аутентификаций

**Database:**
- [ ] Strong password для PostgreSQL
- [ ] Отключение удаленного доступа (только localhost)

**Network:**
- [ ] Firewall (открыть только порт 8000 для локальной сети)

**Electron:**
- [ ] Code signing (подпись установщика) - опционально
- [ ] Отключение DevTools в production

---

## Чек-лист готовности к production

### Сервер
- [ ] Docker и Docker Compose установлены
- [ ] `.env.production` настроен с сильными паролями
- [ ] Firewall настроен (порт 8000 для локальной сети)
- [ ] Backup настроен
- [ ] Логи настроены и ротируются
- [ ] Тестовые пользователи созданы

### Клиенты
- [ ] Electron установщик собран
- [ ] Правильный API URL в `.env.production`
- [ ] Инструкция по установке готова

### Документация
- [ ] DEPLOYMENT.md
- [ ] CLIENT_INSTALL.md
- [ ] UPDATE.md
- [ ] USER_GUIDE.md
- [ ] ADMIN_GUIDE.md

### Тестирование
- [ ] Развертывание сервера протестировано
- [ ] Установка клиента протестирована
- [ ] CRUD операции работают
- [ ] Файлы загружаются/скачиваются
- [ ] Одновременная работа нескольких пользователей
- [ ] Backup и restore протестированы

---

## Системные требования

**Сервер:**
- OS: Windows Server 2019+ или Ubuntu 20.04+
- CPU: 4 cores
- RAM: 8 GB
- HDD: 100 GB (SSD рекомендуется)

**Клиент:**
- OS: Windows 10/11 (64-bit)
- CPU: 2 cores
- RAM: 4 GB
- HDD: 500 MB

---

## Порты

| Сервис | Порт | Доступ |
|--------|------|--------|
| Backend API | 8000 | Локальная сеть |
| PostgreSQL | 5432 | Только localhost |

---

**Контакты:**
- Разработчик: NazarovEvgn
- Репозиторий: https://github.com/NazarovEvgn/deltica
