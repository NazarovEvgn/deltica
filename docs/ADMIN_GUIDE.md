# Руководство администратора Deltica

## Содержание
1. [Обязанности администратора](#обязанности-администратора)
2. [Управление пользователями](#управление-пользователями)
3. [Создание резервных копий](#создание-резервных-копий)
4. [Мониторинг системы](#мониторинг-системы)
5. [Управление оборудованием](#управление-оборудованием)
6. [Работа с архивом](#работа-с-архивом)
7. [Управление документами](#управление-документами)
8. [Обслуживание базы данных](#обслуживание-базы-данных)
9. [Анализ логов](#анализ-логов)
10. [Устранение типовых проблем](#устранение-типовых-проблем)
11. [Регламентные работы](#регламентные-работы)
12. [Безопасность](#безопасность)

---

## Обязанности администратора

### Ежедневные задачи

- ✅ Проверка доступности системы (утром)
- ✅ Мониторинг использования ресурсов (CPU, RAM, HDD)
- ✅ Просмотр логов на наличие ошибок
- ✅ Проверка статуса контейнеров Docker
- ✅ Ответы на запросы пользователей

### Еженедельные задачи

- ✅ Создание резервной копии базы данных (backup)
- ✅ Проверка свободного места на диске
- ✅ Анализ производительности системы
- ✅ Обновление статистики использования

### Ежемесячные задачи

- ✅ Полная резервная копия (БД + файлы)
- ✅ Ротация логов (удаление старых)
- ✅ Проверка обновлений системы
- ✅ Ревизия учетных записей пользователей
- ✅ Анализ метрик производительности

### Ежеквартальные задачи

- ✅ Обновление паролей администраторов
- ✅ Аудит безопасности
- ✅ Планирование обновлений
- ✅ Отчет о работе системы

---

## Управление пользователями

### Структура пользователей

Deltica использует **файловый подход** к управлению пользователями через YAML-конфигурацию.

**Файл конфигурации**: `config/users_config.yaml`

### Просмотр текущих пользователей

#### Через базу данных

```bash
# Подключение к PostgreSQL
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod

# SQL запрос
SELECT id, username, role, full_name, department FROM users ORDER BY role, username;

# Выход
\q
```

#### Через Python скрипт

```bash
# На сервере
cd /opt/deltica
docker exec -it deltica_backend uv run python -c "
from backend.core.database import SessionLocal
from backend.app.models import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f'{user.username:20} {user.role:10} {user.full_name:30} {user.department}')
db.close()
"
```

### Добавление нового пользователя

#### Шаг 1: Редактирование конфигурации

```bash
# Открыть файл конфигурации
nano config/users_config.yaml
```

**Пример добавления администратора:**

```yaml
users:
  - username: "admin"
    password: "admin123"  # ИЗМЕНИТЕ ПАРОЛЬ!
    role: "admin"
    full_name: "Администратор Системы"
    department: "ИТ отдел"

  - username: "new_admin"
    password: "СИЛЬНЫЙ_ПАРОЛЬ"
    role: "admin"
    full_name: "Новый Администратор"
    department: "ИТ отдел"
```

**Пример добавления лаборанта:**

```yaml
  - username: "ivanov"
    password: "lab123"  # ИЗМЕНИТЕ ПАРОЛЬ!
    role: "laborant"
    full_name: "Иванов И.И."
    department: "lbr"  # Технический код подразделения
```

**Коды подразделений:**
- `lbr` - Лаборатория (ЛБР)
- `gtl` - ГТЛ
- `smtsik` - СМТСиК
- `ciks` - ЦИКС
- `ctd` - ЦТД
- `gro` - ГРО
- `tro` - ТрО
- `opo` - ОПО
- `oitzs` - ОИТЗС
- `krc` - КРЦ
- `aho` - АХО
- `other` - Другие подразделения

#### Шаг 2: Синхронизация с базой данных

```bash
# Запуск скрипта синхронизации
docker exec -it deltica_backend uv run python backend/scripts/sync_users.py
```

**Вывод при успехе:**
```
Created user: new_admin (admin)
Synced user: ivanov (laborant)
Total users in database: 15
```

#### Шаг 3: Проверка

```bash
# Проверка через API
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"new_admin","password":"СИЛЬНЫЙ_ПАРОЛЬ"}'

# Должен вернуться JWT token
```

### Изменение пароля пользователя

#### Способ 1: Через конфигурацию (рекомендуется)

1. Отредактируйте `config/users_config.yaml`
2. Измените пароль для нужного пользователя
3. Запустите `sync_users.py`

#### Способ 2: Через SQL (прямое изменение)

```bash
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod
```

```sql
-- Генерация хэша пароля (используйте Python для генерации bcrypt hash)
-- UPDATE users SET hashed_password = '$2b$12$HASH_HERE' WHERE username = 'ivanov';
```

**Генерация bcrypt hash (Python):**

```bash
docker exec -it deltica_backend uv run python -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('NEW_PASSWORD'))
"
```

Скопируйте полученный хэш и выполните UPDATE запрос.

### Удаление пользователя

#### Способ 1: Мягкое удаление (деактивация)

Удалите пользователя из `users_config.yaml` и запустите `sync_users.py`.

**⚠️ Важно**: Скрипт `sync_users.py` НЕ удаляет пользователей из БД, только создает/обновляет.

#### Способ 2: Жесткое удаление из БД

```sql
-- ОСТОРОЖНО! Необратимая операция
DELETE FROM users WHERE username = 'old_user';
```

### Смена роли пользователя

1. Отредактируйте `config/users_config.yaml`
2. Измените `role: "laborant"` на `role: "admin"` (или наоборот)
3. Запустите `sync_users.py`

**Пример:**

```yaml
# Было:
  - username: "ivanov"
    role: "laborant"

# Стало:
  - username: "ivanov"
    role: "admin"
```

---

## Создание резервных копий

### Автоматический backup через интерфейс

1. Войдите как администратор
2. Нажмите **"Админ панель"** → **"Backup БД"**
3. Откроется панель управления backup
4. Нажмите кнопку **"Создать backup"**
5. Дождитесь завершения (обычно 10-30 секунд)
6. Файл сохранится в `backend/backups/`

**Формат имени файла**: `backup_YYYYMMDD_HHMMSS.sql`

**Пример**: `backup_20251026_150000.sql`

### Ручной backup через командную строку

#### Полный backup

```bash
# На сервере
cd /opt/deltica

# 1. Backup PostgreSQL базы данных
docker exec deltica_postgres pg_dump -U deltica_user deltica_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Backup загруженных файлов
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/

# 3. Backup закрепленных документов
tar -czf pinned_docs_backup_$(date +%Y%m%d).tar.gz backend/uploads/pinned_documents/

# 4. Backup конфигураций
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ .env.production

# 5. Перемещение в папку backup
mkdir -p /backup/deltica/
mv *.sql *.tar.gz /backup/deltica/
```

#### Автоматизация через cron

Создайте скрипт `/opt/deltica/backup.sh`:

```bash
#!/bin/bash
set -e

BACKUP_DIR="/backup/deltica"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание папки
mkdir -p $BACKUP_DIR

# Backup БД
docker exec deltica_postgres pg_dump -U deltica_user deltica_prod > $BACKUP_DIR/backup_${DATE}.sql

# Backup файлов (каждые 7 дней)
DAY_OF_WEEK=$(date +%u)
if [ $DAY_OF_WEEK -eq 7 ]; then
    tar -czf $BACKUP_DIR/uploads_backup_${DATE}.tar.gz backend/uploads/
fi

# Удаление старых backup (старше 30 дней)
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Настройка cron:**

```bash
# Редактирование crontab
crontab -e

# Добавить строку (backup каждый день в 2:00 ночи)
0 2 * * * /opt/deltica/backup.sh >> /var/log/deltica_backup.log 2>&1
```

### Восстановление из backup

#### Восстановление базы данных

```bash
# 1. Остановка backend
docker stop deltica_backend

# 2. Восстановление БД
docker exec -i deltica_postgres psql -U deltica_user deltica_prod < /backup/deltica/backup_20251026_150000.sql

# 3. Запуск backend
docker start deltica_backend
```

#### Восстановление файлов

```bash
# Распаковка архива
tar -xzf /backup/deltica/uploads_backup_20251026.tar.gz -C /opt/deltica/
```

### Просмотр истории backup

История backup хранится в таблице `backup_history`:

```sql
SELECT * FROM backup_history ORDER BY created_at DESC LIMIT 10;
```

Или через интерфейс:
- Админ панель → Backup БД → История backup

---

## Мониторинг системы

### Панель мониторинга

1. Войдите как администратор
2. Нажмите **"Админ панель"** → **"Мониторинг"**
3. Откроется панель с двумя вкладками:
   - **Статус системы**
   - **Логи**

### Статус системы

#### Отображаемые метрики

**Подключение к БД:**
- 🟢 Подключено
- 🔴 Отключено

**Использование CPU:**
- % загрузки процессора

**Использование RAM:**
- Использовано / Всего (GB)
- % загрузки

**Использование диска:**
- Использовано / Всего (GB)
- % загрузки

**Статистика логов:**
- Размер файла логов
- Количество записей (INFO, WARNING, ERROR)

### Просмотр логов

Вкладка "Логи" отображает последние 100 записей из `backend/logs/deltica.log`.

**Цветовая кодировка:**
- 🔵 **INFO** - информационные сообщения
- 🟡 **WARNING** - предупреждения
- 🔴 **ERROR** - ошибки

**Содержимое логов:**
- Timestamp (дата и время)
- Уровень (level)
- Сообщение (message)
- Пользователь (user) - если применимо
- IP-адрес (ip) - если применимо
- Путь запроса (path) - для HTTP запросов
- Метод (method) - для HTTP запросов
- Статус (status) - код ответа
- Длительность (duration) - время выполнения запроса

### Мониторинг через командную строку

#### Статус контейнеров

```bash
# Список запущенных контейнеров
docker ps

# Использование ресурсов контейнерами
docker stats

# Вывод:
# CONTAINER        CPU %   MEM USAGE / LIMIT     MEM %   NET I/O
# deltica_backend  5.23%   256MB / 8GB          3.20%   1.2kB / 850B
# deltica_postgres 2.10%   512MB / 8GB          6.40%   850B / 1.2kB
```

#### Логи контейнеров

```bash
# Логи backend (последние 100 строк)
docker logs deltica_backend --tail 100

# Логи PostgreSQL
docker logs deltica_postgres --tail 100

# Следить за логами в реальном времени
docker logs -f deltica_backend
```

#### Проверка состояния базы данных

```bash
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod
```

```sql
-- Размер базы данных
SELECT pg_size_pretty(pg_database_size('deltica_prod'));

-- Количество записей в таблицах
SELECT 'equipment' AS table, COUNT(*) FROM equipment
UNION ALL
SELECT 'verification', COUNT(*) FROM verification
UNION ALL
SELECT 'users', COUNT(*) FROM users;

-- Активные подключения
SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'deltica_prod';

-- Медленные запросы (если настроены)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### Проверка использования диска

```bash
# Общее использование
df -h

# Размер папки uploads
du -sh /opt/deltica/backend/uploads

# Размер папки backups
du -sh /opt/deltica/backend/backups

# Размер логов
du -sh /opt/deltica/backend/logs

# Размер Docker volumes
docker system df -v
```

---

## Управление оборудованием

### Массовое добавление оборудования

Для импорта большого количества оборудования из Excel используйте скрипт импорта.

**Документация**: `docs/data_import_guide.md`

**Основные шаги:**

1. Подготовьте Excel файл с данными
2. Отредактируйте `backend/scripts/import_equipment_data.py`
3. Запустите скрипт для генерации SQL
4. Выполните SQL через `execute_import_sql.py`

### Массовое редактирование

Для изменения множества записей используйте SQL запросы:

**Пример 1: Изменить подразделение для группы оборудования**

```sql
-- Перевод всех манометров из ЛБР в ГТЛ
UPDATE equipment
SET equipment_id = (
    SELECT id FROM responsibility
    WHERE responsibility.equipment_id = equipment.id
)
WHERE equipment_name LIKE '%Манометр%';

UPDATE responsibility
SET department = 'gtl'
WHERE equipment_id IN (
    SELECT id FROM equipment WHERE equipment_name LIKE '%Манометр%'
);
```

**Пример 2: Массовая консервация**

```sql
-- Перевести все оборудование определенного типа на консервацию
UPDATE equipment
SET verification_state = 'state_storage'
WHERE equipment_type = 'IO' AND equipment_name LIKE '%Насос%';
```

### Удаление дублей

```sql
-- Поиск дублей по заводскому номеру
SELECT factory_number, COUNT(*)
FROM equipment
GROUP BY factory_number
HAVING COUNT(*) > 1;

-- Удаление дублей (оставляет запись с минимальным ID)
DELETE FROM equipment
WHERE id NOT IN (
    SELECT MIN(id)
    FROM equipment
    GROUP BY factory_number
);
```

---

## Работа с архивом

### Массовое архивирование

Для архивирования группы оборудования используйте SQL:

```sql
-- Пример: Архивировать все оборудование старше 15 лет
-- (Требуется создать функцию или использовать backend API)
```

**Рекомендация**: Используйте интерфейс для архивирования, так как backend обрабатывает связанные данные корректно.

### Очистка архива

Периодически удаляйте старые архивные записи:

```sql
-- Удаление архивных записей старше 5 лет
DELETE FROM archived_equipment
WHERE archived_at < NOW() - INTERVAL '5 years';
```

### Статистика архива

```sql
-- Количество архивных записей по причинам
SELECT archive_reason, COUNT(*)
FROM archived_equipment
GROUP BY archive_reason;

-- Оборудование, архивированное за последний месяц
SELECT COUNT(*)
FROM archived_equipment
WHERE archived_at > NOW() - INTERVAL '1 month';
```

---

## Управление документами

### Загрузка общих документов

1. Войдите как администратор
2. Нажмите кнопку **"Документы"**
3. Нажмите **"Загрузить документ"**
4. Выберите PDF файл (максимум 50 MB)
5. Дождитесь завершения загрузки

**Местоположение файлов**: `backend/uploads/pinned_documents/`

### Управление через файловую систему

```bash
# Просмотр загруженных документов
ls -lh backend/uploads/pinned_documents/

# Добавление документа вручную (не рекомендуется)
cp /path/to/document.pdf backend/uploads/pinned_documents/

# Затем добавьте запись в БД:
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod
INSERT INTO pinned_documents (filename, file_path, uploaded_by, uploaded_at)
VALUES ('document.pdf', 'pinned_documents/document.pdf', 1, NOW());
```

### Удаление документов

Используйте интерфейс для корректного удаления (файл + запись в БД).

---

## Обслуживание базы данных

### Оптимизация производительности

#### VACUUM и ANALYZE

```sql
-- Очистка "мертвых" строк и обновление статистики
VACUUM ANALYZE;

-- Для конкретной таблицы
VACUUM ANALYZE equipment;

-- Полная очистка (требует эксклюзивной блокировки)
VACUUM FULL;
```

#### Переиндексация

```sql
-- Переиндексация всей базы данных
REINDEX DATABASE deltica_prod;

-- Переиндексация таблицы
REINDEX TABLE equipment;
```

#### Настройка автовакуума

```sql
-- Проверка настроек autovacuum
SHOW autovacuum;

-- Изменение параметров (требует перезапуска)
ALTER SYSTEM SET autovacuum_naptime = '5min';
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;
SELECT pg_reload_conf();
```

### Проверка целостности данных

```sql
-- Проверка внешних ключей
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f';

-- Поиск "осиротевших" верификаций
SELECT v.*
FROM verification v
LEFT JOIN equipment e ON v.equipment_id = e.id
WHERE e.id IS NULL;

-- Поиск оборудования без верификации
SELECT e.*
FROM equipment e
LEFT JOIN verification v ON e.id = v.equipment_id
WHERE v.id IS NULL;
```

### Мониторинг производительности запросов

```sql
-- Включение pg_stat_statements (если не включен)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Топ медленных запросов
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Сброс статистики
SELECT pg_stat_statements_reset();
```

---

## Анализ логов

### Структура логов

**Файл логов**: `backend/logs/deltica.log`

**Формат**: JSON (одна строка = одна запись)

**Пример записи:**

```json
{
  "timestamp": "2025-10-26T15:30:00.123Z",
  "level": "INFO",
  "message": "HTTP request",
  "user": "admin",
  "ip": "192.168.1.50",
  "method": "GET",
  "path": "/main-table/",
  "status": 200,
  "duration": 0.045
}
```

### Поиск в логах

```bash
# Последние 100 строк
tail -n 100 backend/logs/deltica.log

# Поиск ошибок
grep '"level":"ERROR"' backend/logs/deltica.log

# Поиск по пользователю
grep '"user":"admin"' backend/logs/deltica.log

# Поиск медленных запросов (более 1 секунды)
grep '"duration":[1-9]' backend/logs/deltica.log

# Количество запросов по эндпоинтам
grep '"path"' backend/logs/deltica.log | cut -d'"' -f8 | sort | uniq -c | sort -rn

# Количество ошибок по дням
grep '"level":"ERROR"' backend/logs/deltica.log | cut -d'"' -f4 | cut -d'T' -f1 | uniq -c
```

### Анализ популярных запросов

```bash
# Топ-10 самых частых эндпоинтов
grep '"path"' backend/logs/deltica.log | \
  jq -r '.path' | \
  sort | uniq -c | sort -rn | head -10
```

### Анализ ошибок аутентификации

```bash
# Неудачные попытки входа
grep 'Authentication failed' backend/logs/deltica.log | \
  jq -r '[.timestamp, .user, .ip] | @csv'
```

---

## Устранение типовых проблем

### Проблема 1: Сервер не отвечает

**Диагностика:**

```bash
# Проверка статуса контейнеров
docker ps -a

# Проверка логов
docker logs deltica_backend --tail 50
```

**Решение:**

```bash
# Перезапуск контейнеров
docker compose restart

# Или полный перезапуск
docker compose down
docker compose up -d
```

### Проблема 2: База данных не отвечает

**Диагностика:**

```bash
# Проверка статуса PostgreSQL
docker logs deltica_postgres --tail 50

# Попытка подключения
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod
```

**Решение:**

```bash
# Перезапуск PostgreSQL
docker restart deltica_postgres

# Если не помогает - проверка коррупции
docker exec -it deltica_postgres pg_isready
```

### Проблема 3: Медленная работа системы

**Диагностика:**

```bash
# Использование ресурсов
docker stats

# Размер базы данных
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod -c "SELECT pg_size_pretty(pg_database_size('deltica_prod'));"
```

**Решение:**

```sql
-- Очистка и оптимизация
VACUUM ANALYZE;
REINDEX DATABASE deltica_prod;
```

### Проблема 4: Переполнение диска

**Диагностика:**

```bash
df -h
du -sh /opt/deltica/backend/uploads
du -sh /opt/deltica/backend/logs
```

**Решение:**

```bash
# Очистка старых backup
find /opt/deltica/backend/backups -name "*.sql" -mtime +30 -delete

# Ротация логов
truncate -s 0 /opt/deltica/backend/logs/deltica.log

# Очистка Docker кэша
docker system prune -a
```

### Проблема 5: Пользователь не может войти

**Диагностика:**

```bash
# Проверка пользователя в БД
docker exec -it deltica_postgres psql -U deltica_user -d deltica_prod -c "SELECT username, role FROM users WHERE username='ivanov';"

# Проверка логов аутентификации
grep 'Authentication' backend/logs/deltica.log | tail -20
```

**Решение:**

```bash
# Сброс пароля через sync_users.py
# 1. Отредактируйте config/users_config.yaml
# 2. Запустите:
docker exec -it deltica_backend uv run python backend/scripts/sync_users.py
```

---

## Регламентные работы

### Еженедельный чек-лист

```
□ Создать backup базы данных
□ Проверить свободное место на диске (минимум 10 GB)
□ Просмотреть логи на наличие ERROR
□ Проверить статус контейнеров (должны быть "Up")
□ Убедиться, что автовакуум работает
```

### Ежемесячный чек-лист

```
□ Полный backup (БД + файлы)
□ Удаление backup старше 30 дней
□ Ротация логов (архивирование старых)
□ Проверка обновлений системы
□ Ревизия пользователей (удалить неактивных)
□ Анализ производительности (медленные запросы)
□ Проверка размера базы данных
□ Оптимизация (VACUUM, REINDEX)
```

### Ежеквартальный чек-лист

```
□ Смена паролей администраторов
□ Аудит безопасности (проверка прав доступа)
□ Планирование обновлений
□ Отчет о работе системы (uptime, ошибки, использование)
□ Проверка резервных копий (тестовое восстановление)
□ Обновление документации
```

---

## Безопасность

### Рекомендации по безопасности

#### 1. Пароли

- ✅ Используйте сильные пароли (минимум 16 символов)
- ✅ Меняйте пароли каждые 90 дней
- ✅ Не используйте одинаковые пароли для разных аккаунтов
- ✅ Не храните пароли в открытом виде

#### 2. Доступ к серверу

- ✅ Используйте SSH ключи вместо паролей
- ✅ Отключите root login через SSH
- ✅ Включите firewall и разрешите только нужные порты
- ✅ Регулярно проверяйте логи доступа

#### 3. База данных

- ✅ PostgreSQL доступен только из Docker сети (не снаружи)
- ✅ Используйте сильный пароль для БД
- ✅ Регулярно создавайте backup
- ✅ Храните backup в безопасном месте (не на том же сервере)

#### 4. Приложение

- ✅ JWT токены с ограниченным сроком действия (24 часа)
- ✅ CORS настроен на конкретные домены
- ✅ Валидация всех входных данных
- ✅ Защита от SQL injection (через ORM)

### Проверка безопасности

```bash
# Проверка открытых портов
netstat -tuln | grep LISTEN

# Должны быть открыты только:
# 8000 (API)
# 22 (SSH)

# Проверка последних входов
last -20

# Проверка неудачных попыток входа
lastb -20
```

---

## Контакты

- **Разработчик**: NazarovEvgn
- **Репозиторий**: https://github.com/NazarovEvgn/deltica
- **Issues**: https://github.com/NazarovEvgn/deltica/issues

---

**Дата последнего обновления**: 26.10.2025
**Версия документа**: 1.0
