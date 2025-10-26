# Руководство по обновлению системы Deltica

## Содержание
1. [Общие принципы обновления](#общие-принципы-обновления)
2. [Подготовка к обновлению](#подготовка-к-обновлению)
3. [Обновление backend (сервер)](#обновление-backend-сервер)
4. [Обновление клиентских приложений](#обновление-клиентских-приложений)
5. [Откат к предыдущей версии](#откат-к-предыдущей-версии)
6. [Проверка после обновления](#проверка-после-обновления)
7. [Устранение проблем при обновлении](#устранение-проблем-при-обновлении)

---

## Общие принципы обновления

### Порядок обновления компонентов

**Правильная последовательность:**

1. ✅ **Создание резервной копии** (backup) базы данных и файлов
2. ✅ **Обновление backend** (сервер)
3. ✅ **Проверка работоспособности** backend
4. ✅ **Обновление клиентских приложений** (на всех рабочих станциях)

**❌ Неправильно:**
- Обновлять клиенты до обновления сервера
- Пропускать создание backup
- Обновлять в рабочее время без предупреждения

### Рекомендуемое время обновления

- **Будние дни**: После 18:00 (конец рабочего дня)
- **Выходные дни**: В любое время
- **Длительность**: Backend обновление ~10-15 минут, клиенты ~5 минут на каждую машину

### Уведомление пользователей

За 24 часа до обновления:
1. Отправить уведомление всем пользователям
2. Указать дату и время обновления
3. Предупредить о временной недоступности системы
4. Попросить сохранить незавершенную работу

**Пример уведомления:**
```
УВЕДОМЛЕНИЕ ОБ ОБНОВЛЕНИИ СИСТЕМЫ DELTICA

Дата: 27.10.2025
Время: 18:00 - 18:30 МСК

Будет проведено плановое обновление системы Deltica до версии 1.1.0.

Во время обновления система будет недоступна около 15-20 минут.

Пожалуйста, завершите работу и сохраните все данные до 18:00.

После завершения обновления вам потребуется обновить клиентское приложение.
Инструкции будут высланы дополнительно.

С уважением,
Отдел ИТ
```

---

## Подготовка к обновлению

### 1. Проверка текущей версии

#### Backend (сервер)

```bash
# Подключение к серверу через SSH
ssh user@server-ip

# Переход в папку проекта
cd /opt/deltica

# Проверка текущей версии
git log -1 --oneline
```

#### Клиент (Windows)

1. Откройте Deltica
2. Нажмите `F12` (DevTools)
3. Перейдите в Console
4. Посмотрите версию в footer или в заголовке окна

### 2. Создание полного backup

**Автоматический backup через интерфейс:**

1. Войдите как администратор
2. Откройте "Админ панель" → "Backup БД"
3. Нажмите "Создать backup"
4. Дождитесь завершения
5. Скачайте backup файл на локальный компьютер

**Ручной backup через командную строку:**

```bash
# На сервере

# 1. Backup PostgreSQL базы данных
docker exec deltica_postgres pg_dump -U deltica_user deltica_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Backup загруженных файлов
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/uploads/

# 3. Backup закрепленных документов
tar -czf pinned_docs_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/uploads/pinned_documents/

# 4. Backup логов
tar -czf logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/logs/

# 5. Копирование backup в безопасное место
mkdir -p /backup/deltica/
mv *.sql *.tar.gz /backup/deltica/
```

### 3. Проверка свободного места на диске

```bash
# Проверка свободного места
df -h

# Должно быть минимум 5 GB свободного места
```

### 4. Остановка backend (на время обновления)

```bash
cd /opt/deltica
docker compose down
```

---

## Обновление backend (сервер)

### Способ 1: Обновление через Git (рекомендуется)

```bash
# 1. Подключение к серверу
ssh user@server-ip

# 2. Переход в папку проекта
cd /opt/deltica

# 3. Проверка текущей ветки
git branch

# 4. Получение последних изменений
git fetch origin

# 5. Проверка доступных версий
git tag

# 6. Переключение на нужную версию (например, v1.1.0)
git checkout v1.1.0

# Или обновление до последнего коммита в main
git checkout main
git pull origin main

# 7. Пересборка Docker образа
docker compose build

# 8. Запуск обновленных контейнеров
docker compose up -d

# 9. Просмотр логов для проверки
docker compose logs -f
```

### Способ 2: Обновление через архив

```bash
# 1. Остановка контейнеров
cd /opt/deltica
docker compose down

# 2. Создание backup текущего кода
tar -czf deltica_old_$(date +%Y%m%d).tar.gz .

# 3. Скачивание новой версии
curl -L https://github.com/NazarovEvgn/deltica/archive/refs/tags/v1.1.0.tar.gz -o deltica_new.tar.gz

# 4. Распаковка (в отдельную папку для безопасности)
mkdir -p /tmp/deltica_new
tar -xzf deltica_new.tar.gz -C /tmp/deltica_new --strip-components=1

# 5. Копирование новых файлов (кроме .env и uploads)
rsync -av --exclude='.env*' --exclude='backend/uploads' --exclude='backend/logs' \
  /tmp/deltica_new/ /opt/deltica/

# 6. Запуск
docker compose up -d --build
```

### Автоматизированный скрипт обновления

Создайте файл `update-server.sh`:

```bash
#!/bin/bash
set -e

echo "=== Deltica Server Update Script ==="
echo "Current time: $(date)"

# 1. Переход в папку проекта
cd /opt/deltica

# 2. Backup перед обновлением
echo "Creating backup..."
docker exec deltica_postgres pg_dump -U deltica_user deltica_prod > /backup/deltica/backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Остановка контейнеров
echo "Stopping containers..."
docker compose down

# 4. Получение обновлений
echo "Fetching updates..."
git fetch origin
git pull origin main

# 5. Пересборка
echo "Rebuilding containers..."
docker compose build

# 6. Запуск
echo "Starting containers..."
docker compose up -d

# 7. Проверка статуса
echo "Checking status..."
sleep 10
docker ps

echo "=== Update completed! ==="
echo "Please check logs: docker compose logs -f"
```

**Использование:**

```bash
# Сделать исполняемым
chmod +x update-server.sh

# Запуск
./update-server.sh
```

---

## Обновление клиентских приложений

### Централизованное обновление (рекомендуется)

#### 1. Сборка нового установщика

На машине разработчика (или сервере сборки):

```bash
# 1. Клонирование репозитория
git clone https://github.com/NazarovEvgn/deltica.git
cd deltica

# 2. Переключение на нужную версию
git checkout v1.1.0

# 3. Сборка Electron установщика
cd frontend
npm install
npm run electron:build:win

# 4. Результат: frontend/dist-electron/Deltica-Setup-1.1.0.exe
```

#### 2. Публикация установщика

**Вариант A: Сетевая папка (рекомендуется для корпоративной сети)**

```bash
# Копирование на сетевой диск
copy frontend\dist-electron\Deltica-Setup-1.1.0.exe \\server\shared\deltica\installers\
```

**Вариант B: GitHub Releases**

1. Перейдите на https://github.com/NazarovEvgn/deltica/releases
2. Нажмите "Draft a new release"
3. Выберите тег `v1.1.0`
4. Загрузите `Deltica-Setup-1.1.0.exe`
5. Опубликуйте релиз

#### 3. Рассылка инструкций пользователям

**Пример инструкции:**

```
ИНСТРУКЦИЯ ПО ОБНОВЛЕНИЮ DELTICA

Уважаемые пользователи!

Обновление сервера завершено. Теперь необходимо обновить клиентское приложение.

ШАГИ:

1. Закройте Deltica (если открыт)

2. Скачайте новый установщик:
   Путь: \\192.168.1.100\shared\deltica\installers\Deltica-Setup-1.1.0.exe

3. Удалите старую версию:
   - Win + R → appwiz.cpl → Найдите Deltica → Удалить

4. Установите новую версию:
   - Запустите Deltica-Setup-1.1.0.exe от имени администратора
   - Следуйте инструкциям установщика

5. Запустите Deltica и войдите с вашими учетными данными

При возникновении проблем обращайтесь в отдел ИТ.

С уважением,
Отдел ИТ
```

### Автоматизированное обновление через скрипт (для IT-отдела)

Создайте PowerShell скрипт `update-client.ps1`:

```powershell
# Deltica Client Update Script
# Автоматизированное обновление клиента на рабочих станциях

param(
    [string]$InstallerPath = "\\server\shared\deltica\installers\Deltica-Setup-1.1.0.exe"
)

Write-Host "=== Deltica Client Update ===" -ForegroundColor Green

# 1. Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Script must be run as Administrator!" -ForegroundColor Red
    exit 1
}

# 2. Закрытие Deltica (если запущен)
Write-Host "Closing Deltica..."
Get-Process | Where-Object {$_.Name -like "*Deltica*"} | Stop-Process -Force

# 3. Удаление старой версии
Write-Host "Uninstalling old version..."
$app = Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*Deltica*"}
if ($app) {
    $app.Uninstall() | Out-Null
}

# 4. Установка новой версии
Write-Host "Installing new version..."
Start-Process -FilePath $InstallerPath -ArgumentList "/S" -Wait

Write-Host "Update completed!" -ForegroundColor Green
```

**Использование через Group Policy или SCCM:**

```powershell
# Развертывание на все компьютеры домена
Invoke-Command -ComputerName (Get-ADComputer -Filter *).Name -FilePath .\update-client.ps1
```

---

## Откат к предыдущей версии

### Откат backend

#### Способ 1: Через Git

```bash
# 1. Остановка контейнеров
docker compose down

# 2. Просмотр истории
git log --oneline -10

# 3. Откат к предыдущему коммиту
git checkout [COMMIT_HASH]

# Или откат к предыдущему тегу
git checkout v1.0.0

# 4. Пересборка
docker compose up -d --build
```

#### Способ 2: Через backup

```bash
# 1. Остановка и удаление контейнеров
docker compose down -v

# 2. Восстановление кода
cd /opt
rm -rf deltica
tar -xzf /backup/deltica/deltica_old_20251026.tar.gz -C deltica

# 3. Восстановление базы данных
cd /opt/deltica
docker compose up -d postgres

# Ожидание запуска PostgreSQL
sleep 10

# Восстановление данных
docker exec -i deltica_postgres psql -U deltica_user deltica_prod < /backup/deltica/backup_20251026_180000.sql

# 4. Запуск backend
docker compose up -d backend
```

### Откат клиента

```powershell
# 1. Удаление новой версии
appwiz.cpl → Удалить Deltica

# 2. Установка старой версии
# Запустите старый установщик (Deltica-Setup-1.0.0.exe)
```

---

## Проверка после обновления

### 1. Проверка статуса контейнеров

```bash
# Статус
docker ps

# Логи
docker compose logs -f backend
docker compose logs -f postgres

# Должны увидеть:
# ✓ "Application startup complete."
# ✓ Нет ошибок миграций
```

### 2. Проверка API через Swagger

```
Откройте: http://[SERVER-IP]:8000/docs
```

Убедитесь, что:
- Swagger UI загружается
- Список эндпоинтов отображается
- Можно выполнить тестовый запрос

### 3. Проверка авторизации

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Должен вернуться JWT token.

### 4. Проверка базы данных

```bash
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod

# SQL запросы
SELECT COUNT(*) FROM equipment;
SELECT COUNT(*) FROM users;
\q
```

### 5. Проверка клиента

1. Запустите Deltica на клиентской машине
2. Войдите с тестовыми credentials
3. Проверьте основные функции:
   - Загрузка таблицы оборудования
   - Фильтрация
   - Создание/редактирование записи
   - Загрузка файла
   - Генерация документа

### 6. Проверка версии в логах

```bash
# Backend
docker compose logs backend | grep "version"

# Клиент
# Откройте Deltica → F12 → Console → проверьте версию
```

---

## Устранение проблем при обновлении

### Проблема 1: Ошибка миграции базы данных

**Симптомы:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxxxx'
```

**Решение:**

```bash
# Проверка текущей ревизии
docker exec -it deltica_backend uv run alembic current

# Просмотр истории
docker exec -it deltica_backend uv run alembic history

# Принудительная установка ревизии (ОСТОРОЖНО!)
docker exec -it deltica_backend uv run alembic stamp head

# Применение миграций заново
docker exec -it deltica_backend uv run alembic upgrade head
```

### Проблема 2: Контейнер падает после обновления

**Диагностика:**

```bash
# Логи
docker logs deltica_backend --tail 100

# Проверка конфигурации
docker inspect deltica_backend
```

**Решение:**

```bash
# Полная пересборка
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Проблема 3: Клиенты не могут подключиться после обновления сервера

**Причина**: Несовместимость API

**Решение**: Убедитесь, что все клиенты обновлены до совместимой версии.

**Временное решение**: Откатите backend к предыдущей версии.

### Проблема 4: Потеря данных после обновления

**Причина**: Не был создан backup или ошибка восстановления

**Решение:**

```bash
# Восстановление из автоматического backup (если есть)
ls -la backend/backups/

# Восстановление последнего backup
docker exec -i deltica_postgres psql -U deltica_user deltica_prod < backend/backups/backup_latest.sql
```

### Проблема 5: Медленная работа после обновления

**Диагностика:**

```bash
# Использование ресурсов
docker stats

# Размер базы данных
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod -c "SELECT pg_size_pretty(pg_database_size('deltica_prod'));"
```

**Решение:**

```sql
-- Переиндексация базы данных
REINDEX DATABASE deltica_prod;

-- Обновление статистики
VACUUM ANALYZE;
```

---

## Журнал обновлений (Changelog)

### v1.1.0 (Планируемая)

**Новые функции:**
- Добавлена поддержка экспорта в Excel
- Улучшена производительность RevoGrid
- Добавлены уведомления о истечении сроков поверки

**Исправления:**
- Исправлена ошибка при загрузке больших файлов
- Улучшена обработка Cyrillic символов

**Миграции:**
- Добавлена таблица `notifications`
- Добавлено поле `notification_enabled` в `users`

### v1.0.0 (Текущая)

**Функции:**
- Docker контейнеризация
- Electron desktop приложение
- CRUD операции для оборудования
- Архивирование
- Генерация документов
- Backup база данных
- Мониторинг системы

---

## Контрольный список обновления

### Перед обновлением
- [ ] Уведомить пользователей за 24 часа
- [ ] Создать backup базы данных
- [ ] Создать backup загруженных файлов
- [ ] Проверить свободное место на диске (минимум 5 GB)
- [ ] Запланировать время обновления (нерабочие часы)

### Обновление backend
- [ ] Подключиться к серверу через SSH
- [ ] Остановить контейнеры
- [ ] Обновить код (git pull или скачать архив)
- [ ] Пересобрать Docker образы
- [ ] Запустить контейнеры
- [ ] Проверить логи на ошибки
- [ ] Протестировать API через Swagger

### Обновление клиентов
- [ ] Собрать новый установщик
- [ ] Разместить на сетевом диске / GitHub Releases
- [ ] Отправить инструкции пользователям
- [ ] Помочь пользователям с обновлением при необходимости

### После обновления
- [ ] Проверить работу на тестовом аккаунте
- [ ] Убедиться, что все функции работают
- [ ] Собрать feedback от пользователей
- [ ] Задокументировать проблемы (если были)
- [ ] Обновить Changelog

---

## Контакты

- **Разработчик**: NazarovEvgn
- **Репозиторий**: https://github.com/NazarovEvgn/deltica

---

**Дата последнего обновления**: 26.10.2025
**Версия документа**: 1.0
