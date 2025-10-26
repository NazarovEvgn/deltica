# Руководство по развертыванию Deltica на сервере

## Содержание
1. [Системные требования](#системные-требования)
2. [Подготовка сервера](#подготовка-сервера)
3. [Установка Docker и Docker Compose](#установка-docker-и-docker-compose)
4. [Развертывание Deltica](#развертывание-deltica)
5. [Настройка безопасности](#настройка-безопасности)
6. [Проверка работоспособности](#проверка-работоспособности)
7. [Настройка автозапуска](#настройка-автозапуска)
8. [Устранение неполадок](#устранение-неполадок)

---

## Системные требования

### Минимальные требования
- **OS**: Windows Server 2019+ или Ubuntu 20.04+ LTS
- **CPU**: 4 cores (Intel/AMD x64)
- **RAM**: 8 GB
- **HDD**: 100 GB свободного пространства (SSD настоятельно рекомендуется)
- **Сеть**: Статический IP-адрес в локальной сети

### Рекомендуемые требования
- **RAM**: 16 GB
- **HDD**: 250 GB SSD
- **CPU**: 6 cores или выше

### Расчет дискового пространства
- Система и Docker: 20 GB
- PostgreSQL база данных: 5-10 GB (зависит от объема данных)
- Загруженные файлы (uploads): 30-50 GB
- Backup данных: 20-30 GB
- Логи: 5-10 GB

---

## Подготовка сервера

### Windows Server

#### 1. Обновление системы
```powershell
# Запустите Windows Update
# Настройки → Обновление и безопасность → Центр обновления Windows
```

#### 2. Отключение брандмауэра или открытие портов
```powershell
# Вариант 1: Разрешить входящие подключения на порт 8000
New-NetFirewallRule -DisplayName "Deltica API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Вариант 2: Отключить брандмауэр (НЕ РЕКОМЕНДУЕТСЯ в production)
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
```

#### 3. Установка OpenSSH (для удаленного управления)
```powershell
# Установка OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Запуск и автозапуск
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
```

### Ubuntu Server

#### 1. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Настройка firewall
```bash
# Установка UFW (если не установлен)
sudo apt install ufw -y

# Разрешение SSH
sudo ufw allow 22/tcp

# Разрешение Deltica API
sudo ufw allow 8000/tcp

# Включение firewall
sudo ufw enable
```

#### 3. Установка необходимых утилит
```bash
sudo apt install -y curl git nano htop
```

---

## Установка Docker и Docker Compose

### Windows Server

#### Вариант 1: Docker Desktop (рекомендуется)

1. Скачайте Docker Desktop для Windows с официального сайта: https://www.docker.com/products/docker-desktop/
2. Запустите установщик `Docker Desktop Installer.exe`
3. Следуйте инструкциям установщика
4. После установки перезагрузите сервер
5. Запустите Docker Desktop и дождитесь полной загрузки

**Проверка установки:**
```powershell
docker --version
docker-compose --version
```

#### Вариант 2: Docker Engine (через WSL2)

```powershell
# Включение WSL2
wsl --install

# Установка Ubuntu в WSL2
wsl --install -d Ubuntu

# Следуйте инструкциям для Ubuntu Server ниже внутри WSL2
```

### Ubuntu Server

#### Установка Docker Engine

```bash
# Удаление старых версий
sudo apt remove docker docker-engine docker.io containerd runc || true

# Установка зависимостей
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Добавление официального GPG ключа Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Добавление репозитория Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Запуск Docker
sudo systemctl start docker
sudo systemctl enable docker

# Добавление пользователя в группу docker (для работы без sudo)
sudo usermod -aG docker $USER

# Перелогиньтесь для применения изменений группы
exit
# Войдите снова через SSH
```

#### Проверка установки

```bash
docker --version
docker compose version

# Тестовый запуск
docker run hello-world
```

---

## Развертывание Deltica

### 1. Клонирование репозитория

```bash
# Создание директории для проекта
mkdir -p /opt/deltica
cd /opt/deltica

# Клонирование репозитория
git clone https://github.com/NazarovEvgn/deltica.git .

# Или скачивание через архив (если нет git)
# curl -L https://github.com/NazarovEvgn/deltica/archive/refs/heads/main.zip -o deltica.zip
# unzip deltica.zip
# mv deltica-main/* .
```

### 2. Настройка переменных окружения

```bash
# Копирование шаблона
cp .env.production.example .env.production

# Редактирование файла (nano или vim)
nano .env.production
```

**Содержимое `.env.production`:**

```bash
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=deltica_prod
DB_USER=deltica_user
DB_PASSWORD=ИЗМЕНИТЕ_НА_СИЛЬНЫЙ_ПАРОЛЬ_12345

# Backend Configuration
SECRET_KEY=ИЗМЕНИТЕ_НА_СЛУЧАЙНУЮ_СТРОКУ_МИНИМУМ_32_СИМВОЛА

# Рекомендации по паролям:
# - DB_PASSWORD: минимум 16 символов, буквы, цифры, спецсимволы
# - SECRET_KEY: минимум 32 символа, случайная строка
```

**Генерация сильного SECRET_KEY:**

```bash
# Linux/macOS
openssl rand -hex 32

# PowerShell (Windows)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### 3. Создание необходимых директорий

```bash
# Создание директорий для volumes
mkdir -p backend/uploads
mkdir -p backend/backups
mkdir -p backend/logs
mkdir -p backend/generated_documents

# Установка прав доступа (только для Linux)
chmod -R 755 backend/uploads
chmod -R 755 backend/backups
chmod -R 755 backend/logs
chmod -R 755 backend/generated_documents
```

### 4. Сборка и запуск контейнеров

#### Linux (Ubuntu)

```bash
# Сборка образов
docker compose build

# Запуск в фоновом режиме
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка просмотра логов: Ctrl+C
```

#### Windows (PowerShell)

```powershell
# Сборка образов
docker-compose build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

### 5. Проверка статуса контейнеров

```bash
# Список запущенных контейнеров
docker ps

# Вывод должен показывать два контейнера:
# - deltica_postgres (PostgreSQL 17)
# - deltica_backend (FastAPI)
```

**Ожидаемый вывод:**
```
CONTAINER ID   IMAGE                  STATUS         PORTS
xxxxxxxxxxxx   deltica_backend        Up 2 minutes   0.0.0.0:8000->8000/tcp
xxxxxxxxxxxx   postgres:17-alpine     Up 2 minutes   0.0.0.0:5432->5432/tcp
```

### 6. Проверка логов

```bash
# Логи backend
docker logs deltica_backend

# Логи PostgreSQL
docker logs deltica_postgres

# Должны увидеть:
# ✓ "Waiting for PostgreSQL..."
# ✓ "Applying database migrations..."
# ✓ "Seeding initial users..."
# ✓ "Starting backend..."
# ✓ "Application startup complete."
```

---

## Настройка безопасности

### 1. Изменение стандартных портов (опционально)

Если требуется изменить порт API с 8000 на другой:

**Редактирование `docker-compose.yml`:**

```yaml
services:
  backend:
    ports:
      - "9000:8000"  # Внешний порт 9000, внутренний 8000
```

### 2. Ограничение доступа к PostgreSQL

По умолчанию PostgreSQL доступен только внутри Docker сети. Для дополнительной безопасности можно закрыть внешний порт:

**Редактирование `docker-compose.yml`:**

```yaml
services:
  postgres:
    # Закомментировать или удалить секцию ports
    # ports:
    #   - "5432:5432"
```

### 3. Настройка firewall (Linux)

```bash
# Разрешить только локальную сеть (пример для сети 192.168.1.0/24)
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Запретить доступ из других сетей
sudo ufw deny 8000/tcp
```

### 4. Регулярное обновление паролей

Рекомендуется менять `DB_PASSWORD` и `SECRET_KEY` каждые 90 дней.

**Процедура смены пароля БД:**

```bash
# 1. Остановить контейнеры
docker compose down

# 2. Удалить volume PostgreSQL (ВНИМАНИЕ: потеря данных!)
docker volume rm deltica_postgres_data

# 3. Изменить DB_PASSWORD в .env.production

# 4. Запустить контейнеры заново
docker compose up -d
```

---

## Проверка работоспособности

### 1. Проверка API через браузер

Откройте в браузере на любом компьютере в сети:

```
http://[IP-АДРЕС-СЕРВЕРА]:8000/docs
```

Пример:
```
http://192.168.1.100:8000/docs
```

Должна открыться страница **Swagger UI** с документацией API.

### 2. Проверка авторизации

#### Через Swagger UI:

1. Перейдите на `/docs`
2. Найдите эндпоинт `POST /auth/login`
3. Нажмите "Try it out"
4. Введите credentials:
   - **username**: `admin`
   - **password**: `admin123`
5. Нажмите "Execute"
6. Должен вернуться JWT token

#### Через curl (Linux):

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 3. Проверка базы данных

```bash
# Подключение к PostgreSQL контейнеру
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod

# SQL запросы для проверки
\dt  # Список таблиц

SELECT COUNT(*) FROM users;  # Количество пользователей (должно быть >= 1)

SELECT username, role FROM users;  # Список пользователей

\q  # Выход
```

### 4. Проверка файловой системы

```bash
# Проверка созданных директорий
ls -la backend/uploads
ls -la backend/backups
ls -la backend/logs

# Проверка логов приложения
tail -f backend/logs/deltica.log
```

---

## Настройка автозапуска

### Ubuntu Server (systemd)

Docker уже настроен на автозапуск. Контейнеры запустятся автоматически после перезагрузки благодаря `restart: unless-stopped` в `docker-compose.yml`.

**Проверка автозапуска:**

```bash
# Перезагрузка сервера
sudo reboot

# После загрузки - проверка статуса
docker ps
```

### Windows Server

Docker Desktop автоматически запускается при загрузке системы. Контейнеры также запустятся автоматически.

**Дополнительная настройка (если нужно):**

1. Откройте "Диспетчер задач" → вкладка "Автозагрузка"
2. Убедитесь, что "Docker Desktop" включен
3. Перезагрузите сервер для проверки

---

## Устранение неполадок

### Проблема: Контейнер backend падает при запуске

**Причина**: Ошибка в миграциях БД или неправильные credentials.

**Решение:**

```bash
# Просмотр логов
docker logs deltica_backend

# Если ошибка в миграциях - пересоздать БД
docker compose down
docker volume rm deltica_postgres_data
docker compose up -d
```

### Проблема: Не удается подключиться к API

**Проверка 1: Статус контейнеров**

```bash
docker ps -a
# Убедитесь, что контейнеры в статусе "Up"
```

**Проверка 2: Firewall**

```bash
# Linux
sudo ufw status

# Windows
Get-NetFirewallRule -DisplayName "Deltica API"
```

**Проверка 3: Доступность порта**

```bash
# Linux
netstat -tuln | grep 8000

# Windows
netstat -an | findstr "8000"
```

### Проблема: PostgreSQL не принимает подключения

**Решение:**

```bash
# Проверка health check
docker inspect deltica_postgres | grep -A 10 Health

# Перезапуск контейнера
docker restart deltica_postgres

# Просмотр логов
docker logs deltica_postgres
```

### Проблема: Нехватка дискового пространства

**Очистка Docker кэша:**

```bash
# Удаление неиспользуемых образов
docker image prune -a

# Удаление неиспользуемых volumes
docker volume prune

# Полная очистка (ОСТОРОЖНО!)
docker system prune -a --volumes
```

### Проблема: Медленная работа системы

**Диагностика:**

```bash
# Использование ресурсов контейнерами
docker stats

# Проверка использования диска
df -h

# Проверка использования RAM
free -h
```

**Решения:**

1. Увеличить RAM сервера
2. Использовать SSD вместо HDD
3. Настроить индексы в PostgreSQL
4. Включить логирование медленных запросов

---

## Полезные команды

### Управление контейнерами

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Перезапуск
docker compose restart

# Пересборка после изменений кода
docker compose up -d --build

# Просмотр логов в реальном времени
docker compose logs -f

# Просмотр логов конкретного сервиса
docker compose logs -f backend
```

### Backup и восстановление

```bash
# Backup базы данных
docker exec deltica_postgres pg_dump -U deltica_user deltica_prod > backup_$(date +%Y%m%d).sql

# Восстановление из backup
docker exec -i deltica_postgres psql -U deltica_user deltica_prod < backup_20250126.sql
```

### Обновление системы

```bash
# 1. Создать backup
docker exec deltica_postgres pg_dump -U deltica_user deltica_prod > backup_before_update.sql

# 2. Остановить контейнеры
docker compose down

# 3. Обновить код
git pull origin main

# 4. Пересобрать и запустить
docker compose up -d --build

# 5. Проверить логи
docker compose logs -f
```

---

## Контакты и поддержка

- **Разработчик**: NazarovEvgn
- **Репозиторий**: https://github.com/NazarovEvgn/deltica
- **Issues**: https://github.com/NazarovEvgn/deltica/issues

---

**Дата последнего обновления**: 26.10.2025
