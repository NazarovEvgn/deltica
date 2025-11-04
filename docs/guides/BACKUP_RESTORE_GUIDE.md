# 📦 Инструкция по Backup и восстановлению базы данных Deltica

## 1. Импорт данных из Excel на ИСХОДНОМ сервере

### Если у вас есть XLS файл с данными:

```powershell
cd C:\Projects\deltica

# 1. Положите ваш Excel файл в папку проекта
# Например: C:\Projects\deltica\data.xlsx

# 2. Запустите скрипт импорта (он уже есть в проекте)
uv run python backend/scripts/import_equipment_data.py

# Скрипт спросит путь к файлу:
# Введите: data.xlsx (или полный путь)
```

**Важно:** Скрипт импорта автоматически:
- Конвертирует русские значения в технические (поверка→verification, ЛБР→lbr, СИ→SI)
- Обрабатывает даты и NULL значения
- Создает SQL файл для импорта
- Загружает данные в базу

Подробности в: `docs/data_import_guide.md`

---

## 2. Создание Backup через приложение

### Способ 1: Через Web интерфейс (рекомендуется)

1. Запустите приложение:
   ```powershell
   .\start.ps1
   ```

2. Откройте http://localhost:5173

3. Войдите как **admin** (admin/admin123)

4. Нажмите кнопку **"Backup БД"** (рядом с Архив и Мониторинг)

5. В открывшемся окне нажмите **"Создать backup"**

6. ✅ Backup создан!

### Способ 2: Вручную через командную строку

```powershell
cd C:\Projects\deltica

# Создать backup вручную
uv run python -c "from backend.services.backup import BackupService; BackupService.create_backup(created_by='admin')"
```

---

## 3. Где лежит файл Backup

### 📁 Расположение:

```
C:\Projects\deltica\backend\backups\
```

### 📝 Имя файла:

```
deltica_backup_YYYYMMDD_HHMMSS.sql
```

**Пример:**
```
deltica_backup_20250204_143022.sql
```

### Что внутри файла:

- Полный SQL дамп базы данных PostgreSQL
- Все таблицы (equipment, verification, users, archive и т.д.)
- Все данные
- Структура таблиц
- Индексы и constraints

---

## 4. Копирование Backup на флешку

```powershell
# Скопируйте последний backup на флешку
Copy-Item "C:\Projects\deltica\backend\backups\deltica_backup_*.sql" "E:\backup\" -Recurse

# Или скопируйте всю папку backups
Copy-Item "C:\Projects\deltica\backend\backups" "E:\deltica-deploy\backend\backups" -Recurse
```

**Что взять на флешку:**
1. ✅ Исходный код (см. ЧТО_БРАТЬ_НА_ФЛЕШКУ.txt)
2. ✅ Файл backup: `backend/backups/deltica_backup_*.sql`
3. ✅ Excel файл (если есть): `data.xlsx`

---

## 5. Восстановление Backup на НОВОМ сервере

### Шаг 1: Установите окружение

(См. DEPLOYMENT_GUIDE.md - установка Python, Node.js, PostgreSQL, uv)

### Шаг 2: Создайте ПУСТУЮ базу данных

```powershell
# Откройте pgAdmin или используйте psql
psql -U postgres
```

```sql
-- Создайте базу и пользователя
CREATE DATABASE deltica_db;
CREATE USER deltica_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE deltica_db TO deltica_user;

-- Дайте права на схему public
\c deltica_db
GRANT ALL ON SCHEMA public TO deltica_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO deltica_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO deltica_user;

-- Выход
\q
```

### Шаг 3: НЕ запускайте миграции Alembic!

```powershell
# ❌ НЕ ДЕЛАЙТЕ ЭТО если восстанавливаете из backup:
# uv run alembic upgrade head

# Миграции уже включены в backup файл!
```

### Шаг 4: Восстановите backup

```powershell
cd C:\Projects\deltica

# Способ 1: Через psql (рекомендуется)
psql -U deltica_user -d deltica_db -f backend\backups\deltica_backup_20250204_143022.sql

# Способ 2: Если psql просит пароль каждый раз
$env:PGPASSWORD="your_password"
psql -U deltica_user -d deltica_db -f backend\backups\deltica_backup_20250204_143022.sql
```

**Должно быть примерно так в выводе:**
```
SET
SET
SET
...
CREATE TABLE
ALTER TABLE
COPY 278  (количество записей equipment)
COPY 150  (количество записей verification)
...
CREATE INDEX
ALTER TABLE
```

### Шаг 5: Проверьте восстановление

```powershell
# Подключитесь к БД
psql -U deltica_user -d deltica_db

# Проверьте количество записей
SELECT COUNT(*) FROM equipment;
SELECT COUNT(*) FROM verification;
SELECT COUNT(*) FROM users;

# Должны быть ваши данные!
\q
```

### Шаг 6: Настройте .env

```powershell
cd C:\Projects\deltica
copy .env.example .env
notepad .env
```

**Отредактируйте .env:**
```ini
DB_USER=deltica_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=deltica_db

SECRET_KEY=your-secret-key-here-change-this-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Шаг 7: Установите зависимости

```powershell
# Backend
uv sync

# Frontend
cd frontend
npm install
cd ..
```

### Шаг 8: Запустите приложение

```powershell
.\start.ps1
```

### Шаг 9: Откройте и проверьте

- Откройте: http://localhost:5173
- Войдите: admin / admin123
- **Все ваши данные должны быть на месте!** ✅

---

## 6. Структура файлов для переноса на флешку

```
E:\deltica-deploy\
├── backend/
│   ├── app/
│   ├── core/
│   ├── routes/
│   ├── services/
│   ├── scripts/
│   │   └── import_equipment_data.py   ← Скрипт импорта из Excel
│   ├── alembic/
│   ├── backups/
│   │   └── deltica_backup_20250204_143022.sql   ← ВАШ BACKUP! 🔥
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── src/
│   ├── public/
│   ├── electron/
│   ├── package.json
│   └── package-lock.json
├── config/
├── .env.example
├── start.ps1
├── DEPLOYMENT_GUIDE.md
└── BACKUP_RESTORE_GUIDE.md   ← Этот файл
```

---

## 7. Важные моменты

### ❌ Частые ошибки:

1. **"Ошибка: таблица уже существует"**
   - Причина: Вы запустили `alembic upgrade head` ПЕРЕД восстановлением backup
   - Решение: Пересоздайте БД (`DROP DATABASE deltica_db; CREATE DATABASE deltica_db;`)

2. **"Permission denied"**
   - Причина: Недостаточно прав у пользователя
   - Решение: См. Шаг 2 - выдайте все права

3. **"Relation does not exist"**
   - Причина: Backup не восстановился полностью
   - Решение: Проверьте вывод psql на ошибки при восстановлении

### ✅ Правильная последовательность:

```
1. Создать пустую БД ✅
2. Восстановить backup ✅
3. Настроить .env ✅
4. Установить зависимости ✅
5. Запустить приложение ✅
```

### ❌ НЕ нужно делать:

```
❌ alembic upgrade head  (миграции уже в backup)
❌ seed_users.py         (пользователи уже в backup)
❌ import_equipment_data.py (данные уже в backup)
```

---

## 8. Альтернатива: Импорт Excel на новом сервере

Если по какой-то причине backup не работает, можете использовать Excel импорт:

```powershell
# 1. Установите окружение
# 2. Запустите миграции (создаст структуру)
uv run alembic upgrade head

# 3. Создайте пользователей
uv run python backend/scripts/seed_users.py

# 4. Импортируйте данные из Excel
uv run python backend/scripts/import_equipment_data.py
# Введите путь к вашему Excel файлу
```

---

## 9. Автоматизация backup (опционально)

Чтобы автоматически создавать backup каждый день:

```powershell
# Создайте scheduled task в Windows
# Task Scheduler → Create Basic Task
# Действие: Start a program
# Program: powershell.exe
# Arguments: -File "C:\Projects\deltica\backend\scripts\auto_backup.ps1"
```

---

## 📝 Резюме

### Для ИСХОДНОГО сервера:
1. Импортируйте данные из Excel (если нужно)
2. Создайте backup через приложение (кнопка "Backup БД")
3. Скопируйте `backend/backups/deltica_backup_*.sql` на флешку

### Для НОВОГО сервера:
1. Установите окружение (PostgreSQL, Python, Node.js)
2. Создайте пустую БД `deltica_db`
3. Восстановите backup: `psql -U deltica_user -d deltica_db -f backup.sql`
4. Настройте `.env`
5. Установите зависимости (`uv sync`, `npm install`)
6. Запустите приложение (`.\start.ps1`)

---

**Готово!** Все данные перенесены на новый сервер! 🎉
