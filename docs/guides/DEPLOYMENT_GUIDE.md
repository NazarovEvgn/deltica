# 🚀 Инструкция по развертыванию Deltica на новом сервере/компьютере

## Вариант 1: Через Git (рекомендуется)

### На исходном компьютере:
```bash
# Убедитесь, что все изменения закоммичены
cd C:\Projects\deltica
git status
git add .
git commit -m "Готово к развертыванию"
git push origin main
```

### На новом компьютере:
```bash
# Клонируйте репозиторий
git clone https://github.com/NazarovEvgn/deltica.git
cd deltica
```

## Вариант 2: Через флешку (без Git)

### Что НЕ нужно копировать на флешку:

❌ **Не копируйте эти папки** (они огромные и генерируются автоматически):
```
frontend/node_modules/          # ~500 MB - установятся через npm install
frontend/dist/                  # Build артефакты
frontend/dist-electron/         # Electron builds
backend/__pycache__/            # Python cache
backend/.venv/                  # Virtual environment
backend/venv/                   # Virtual environment
backend/uploads/                # Загруженные файлы (опционально - можно не брать)
backend/backups/                # Backup файлы (опционально)
backend/logs/                   # Log файлы (опционально)
.git/                          # Если не нужна история коммитов
```

### Что НУЖНО скопировать на флешку:

✅ **Копируйте все остальное**:
```
deltica/
├── backend/
│   ├── app/              ✅ Модели и схемы
│   ├── core/             ✅ Конфигурация и main.py
│   ├── routes/           ✅ API endpoints
│   ├── services/         ✅ Бизнес-логика
│   ├── tests/            ✅ Тесты
│   ├── scripts/          ✅ Утилиты (seed_users.py и т.д.)
│   ├── alembic/          ✅ Миграции БД
│   ├── alembic.ini       ✅
│   ├── pyproject.toml    ✅
│   └── uv.lock           ✅
├── frontend/
│   ├── src/              ✅ Исходный код Vue.js
│   ├── public/           ✅ Статические файлы
│   ├── electron/         ✅ Electron файлы
│   ├── build/            ✅ Build скрипты
│   ├── package.json      ✅
│   ├── package-lock.json ✅
│   ├── vite.config.js    ✅
│   └── index.html        ✅
├── config/               ✅ Конфигурационные файлы
├── docs/                 ✅ Документация
├── .env.example          ✅ Пример конфигурации
├── start.ps1             ✅ Скрипт запуска
├── start.bat             ✅ Скрипт запуска
├── start-desktop.ps1     ✅ Electron запуск
├── start-desktop.bat     ✅ Electron запуск
├── CLAUDE.md             ✅ Документация проекта
├── BUILD_INSTRUCTIONS.md ✅
├── DEPLOYMENT_GUIDE.md   ✅ Эта инструкция
└── README.md             ✅ (если есть)
```

### Простой способ копирования (PowerShell):

```powershell
# На исходном компьютере
cd C:\Projects

# Создаем архив без ненужных папок
$exclude = @('node_modules', 'dist', 'dist-electron', '__pycache__', '.venv', 'venv', '.git', 'uploads', 'backups', 'logs')
$source = "deltica"
$destination = "E:\deltica-deploy.zip"  # E: - это флешка

# Копируем папку на флешку (БЕЗ архивации)
robocopy "C:\Projects\deltica" "E:\deltica-deploy" /E /XD node_modules dist dist-electron __pycache__ .venv venv .git uploads backups logs generated_documents /XF *.pyc *.log

# Результат: папка deltica-deploy на флешке (~50-100 MB вместо 800+ MB)
```

### Или через проводник (вручную):

1. Скопируйте всю папку `C:\Projects\deltica` на флешку
2. На флешке удалите тяжелые папки:
   - `frontend/node_modules`
   - `frontend/dist`
   - `frontend/dist-electron`
   - `backend/__pycache__`
   - `backend/.venv` или `backend/venv`
   - `backend/uploads` (если не нужны файлы)

## На новом компьютере - Установка окружения

### 1. Установите необходимое ПО:

**Python 3.13:**
- Скачать: https://www.python.org/downloads/
- При установке: ✅ Add Python to PATH

**Node.js 20.19+ или 22.12+:**
- Скачать: https://nodejs.org/
- LTS версия

**uv (Python package manager):**
```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**PostgreSQL 13+:**
- Скачать: https://www.postgresql.org/download/windows/
- Запомните пароль для пользователя postgres

**Git (опционально, но рекомендуется):**
- Скачать: https://git-scm.com/download/win

### 2. Скопируйте проект с флешки:

```powershell
# Копируйте папку с флешки в рабочую директорию
Copy-Item -Path "E:\deltica-deploy" -Destination "C:\Projects\deltica" -Recurse

# Или если использовали Git клонирование - пропустите этот шаг
```

### 3. Настройте базу данных:

```powershell
# Подключитесь к PostgreSQL (используйте pgAdmin или командную строку)
# Создайте базу данных:
```

```sql
CREATE DATABASE deltica_db;
CREATE USER deltica_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE deltica_db TO deltica_user;
```

### 4. Настройте конфигурацию:

```powershell
cd C:\Projects\deltica

# Скопируйте .env.example в .env
copy .env.example .env

# Отредактируйте .env (используйте notepad или VSCode)
notepad .env
```

**Измените в .env:**
```ini
DB_USER=deltica_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=deltica_db

SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 5. Установите зависимости:

**Backend:**
```powershell
cd C:\Projects\deltica

# uv автоматически создаст виртуальное окружение и установит зависимости
uv sync
```

**Frontend:**
```powershell
cd C:\Projects\deltica\frontend

# Установка зависимостей (может занять 2-5 минут)
npm install
```

### 6. Примените миграции базы данных:

```powershell
cd C:\Projects\deltica

# Проверьте подключение к БД
uv run alembic current

# Примените все миграции
uv run alembic upgrade head
```

### 7. Создайте начальных пользователей:

```powershell
# Создает admin/admin123 и лаборантов
uv run python backend/scripts/seed_users.py
```

### 8. Запустите приложение:

**Вариант 1: Web версия (backend + frontend)**
```powershell
# PowerShell (запускает оба сервера одновременно)
.\start.ps1

# Или в CMD
start.bat
```

**Вариант 2: Desktop версия (Electron)**
```powershell
# PowerShell
.\start-desktop.ps1

# Или в CMD
start-desktop.bat
```

### 9. Откройте приложение:

- **Web версия**: http://localhost:5173
- **Desktop версия**: откроется автоматически
- **API документация**: http://localhost:8000/docs

**Учетные данные:**
- Админ: `admin` / `admin123`
- Лаборант: `ivanov` / `lab123`

## Проверка установки

```powershell
# Проверьте версии
python --version        # Должно быть 3.13
node --version          # Должно быть 20.19+ или 22.12+
uv --version           # Должно быть установлено

# Проверьте PostgreSQL
psql -U postgres -c "SELECT version();"
```

## Troubleshooting

### Ошибка подключения к БД:
```powershell
# Проверьте, что PostgreSQL запущен
# Откройте "Службы" Windows и найдите PostgreSQL

# Или через PowerShell
Get-Service postgresql*
```

### Ошибка "Module not found":
```powershell
# Backend
cd C:\Projects\deltica
uv sync --reinstall

# Frontend
cd C:\Projects\deltica\frontend
npm ci  # Чистая установка
```

### Порты уже заняты:
```powershell
# Проверьте, что порты 5173 и 8000 свободны
netstat -ano | findstr :5173
netstat -ano | findstr :8000

# Убейте процесс если нужно (замените PID на реальный)
taskkill /PID 12345 /F
```

## Размеры для оценки

| Что | Размер |
|-----|--------|
| Исходный код (без node_modules) | ~20-30 MB |
| Backend dependencies (.venv) | ~200 MB |
| Frontend dependencies (node_modules) | ~500 MB |
| **ИТОГО после установки** | ~720-730 MB |
| На флешке (без зависимостей) | ~20-30 MB |

## Быстрая шпаргалка

```powershell
# 1. Скопировать проект с флешки
Copy-Item E:\deltica-deploy C:\Projects\deltica -Recurse

# 2. Создать .env из примера
cd C:\Projects\deltica
copy .env.example .env
notepad .env  # Отредактировать DB credentials

# 3. Установить зависимости
uv sync
cd frontend && npm install && cd ..

# 4. Настроить БД
# (создать базу deltica_db через pgAdmin или psql)

# 5. Миграции и пользователи
uv run alembic upgrade head
uv run python backend/scripts/seed_users.py

# 6. Запустить
.\start.ps1

# 7. Открыть http://localhost:5173
```

## Дополнительно: Production деплой

Если нужен production деплой на Windows Server, смотрите:
- `docs/deployment/production_deployment.md` (если есть)
- Используйте IIS для frontend
- Используйте Windows Service для backend
- Настройте nginx как reverse proxy (опционально)

---

**Готово!** Теперь у вас полностью рабочая среда разработки на новом компьютере.
