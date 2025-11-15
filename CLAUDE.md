# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Deltica - система управления метрологическим оборудованием для нефтегазовых компаний. Отслеживает средства измерений (СИ) и испытательное оборудование (ИО), их графики поверки/калибровки/аттестации.

**Ключевые концепции:**
- **Equipment Types**: СИ (measuring instruments), ИО (testing equipment)
- **Verification**: Периодические процедуры (поверка/калибровка/аттестация) с интервалами
- **User Roles**: Admin (CRUD), Laborant (read-only по отделу)
- **Equipment States**: work/storage/verification/repair/archived
- **Equipment Status**: fit/expired/expiring (автоматический расчет по датам)

## Tech Stack

**Backend:**
- FastAPI + Python 3.13 (uv package manager)
- PostgreSQL + SQLAlchemy ORM + Alembic migrations
- JWT authentication (bcrypt), Windows SSO поддержка
- Structured JSON logging, pg_dump backups

**Frontend:**
- Vue.js 3 + Vite + Naive UI
- RevoGrid (Excel-like таблица с inline editing)
- Axios + JWT interceptors
- PT Astra Sans (корпоративный шрифт)
- Gazprom Neft цвета (#0071BC primary)

**Desktop:**
- Electron v38 (production-ready)
- NSIS + Portable установщики
- Требует `icon.ico` (не PNG!) для сборки
- Backend (FastAPI) - отдельный процесс

**Commercial Build:**
- Server: PyInstaller → `deltica-server.exe` (standalone)
  - Включает `init-database.bat` для автоматической инициализации БД
  - Дамп БД в `database_dumps/deltica_initial.dump` (pg_dump custom format)
- Client: electron-builder → `Deltica-Setup-1.0.0.exe`
  - Диалог настройки сервера при первом запуске (ConfigModal)
  - Сохранение конфигурации в userData/config.json
- Защита: bytecode compilation + ASAR packaging

## Development Commands

### Quick Start
```bash
# Setup
cp .env.example .env  # Edit DB credentials
uv sync
cd frontend && npm install

# Run (web mode)
.\start.ps1  # Windows PowerShell
start.bat    # Windows CMD

# Run (desktop mode)
.\start-desktop.ps1
```

### Backend
```bash
uv run uvicorn backend.core.main:app --reload  # http://localhost:8000
uv run uvicorn backend.core.main:app --reload --port 8001
# API docs: http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm run dev        # http://localhost:5173
npm run build      # Production build
npm run preview    # Preview production
```

### Desktop (Electron)
```bash
# Development
cd frontend
npm run electron:dev

# Production build (ТРЕБУЕТ ADMIN ПРАВ для NSIS)
npm run build && npm run electron:build:win

# Или через PowerShell от администратора
.\build-installer.ps1  # Очищает кэш + собирает

# ВАЖНО: icon.ico должен быть в frontend/public/
```

### Commercial Build
```bash
# Server build (PyInstaller)
.\build-scripts\build-server.ps1
# → dist/Deltica-Server-v1.0.0.zip

# Client build (electron-builder, требует admin)
.\build-scripts\build-client.ps1
# → dist/Deltica-Client-v1.0.0.zip

# Результат:
# dist/Deltica-Server-v1.0.0/ - сервер для установки
# dist/Deltica-Client-v1.0.0/ - установщики + README
```

### Database
```bash
uv run alembic current              # Текущая миграция
uv run alembic history              # История
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head         # Применить миграции
uv run alembic downgrade -1         # Откат

# Database dump для коммерческой сборки
pg_dump -h 127.0.0.1 -p 5432 -U postgres -d deltica_db \
        -F c -b -f backend/database_dumps/deltica_initial.dump
```

### Database Initialization (Commercial Build)
```bash
# В коммерческой сборке (dist/Deltica-Server-v1.0.X/):
# 1. Настроить .env с credentials (DB_HOST=127.0.0.1, НЕ localhost!)
# 2. Запустить init-database.bat (ОДИН РАЗ!)
#
# Скрипт автоматически:
# - Проверяет PostgreSQL (pg_isready)
# - Создает БД если не существует (createdb)
# - Восстанавливает структуру и данные (pg_restore)
#
# Не требует миграций Alembic или seed scripts!
```

**ВАЖНО: PostgreSQL Permissions Issue**

При первом запуске init-database.bat может возникнуть ошибка:
```
pg_restore: error: нет доступа к схеме public
```

**Решение через pgAdmin:**
1. Открыть pgAdmin → Query Tool на `deltica_db`
2. Выполнить:
```sql
GRANT ALL ON SCHEMA public TO deltica_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO deltica_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO deltica_user;
ALTER DATABASE deltica_db OWNER TO deltica_user;
```
3. Перезапустить init-database.bat

### Users
```bash
uv run python backend/scripts/seed_users.py    # admin/admin123
uv run python backend/scripts/sync_users.py    # Sync from config/users_config.yaml
```

### Testing
```bash
uv run pytest                       # All tests (152)
uv run pytest backend/tests/test_files_api.py -v
uv run pytest backend/tests/test_status_calculation.py
```

## Architecture

### Backend Structure
```
backend/
├── core/          # main.py, config, database, logging
├── app/           # models.py (ORM), schemas.py (Pydantic)
├── services/      # Business logic (main_table, archive, backup, documents)
├── routes/        # API endpoints (auth, main_table, files, archive, etc.)
├── middleware/    # logging_middleware.py
├── utils/         # auth.py (JWT, passwords)
├── scripts/       # seed_users.py, sync_users.py, import_equipment_data.py
└── tests/         # 152 tests
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/       # Vue SFC (MainTable, EquipmentModal, ConfigModal, etc.)
│   ├── composables/      # useAuth, useEquipmentMetrics, useEquipmentFilters
│   ├── config/           # api.js (динамическая конфигурация API endpoints)
│   ├── assets/styles/    # fonts.css, colors.css, global.css
│   ├── App.vue           # Root with NConfigProvider + first-run config
│   └── main.js           # Entry, axios config
├── electron/             # main.js, preload.js (ES modules, IPC handlers)
├── public/               # favicon.png, icon.ico, fonts/
├── package.json          # build config in "build" section
└── vite.config.js        # ВАЖНО: base: './' для Electron
```

### Database Schema
```
Equipment ←1:N→ Verification
Equipment ←1:1→ Responsibility (equipment_id FK)
Equipment ←1:1→ Finance (equipment_model_id FK) ⚠️ inconsistent naming
Equipment ←1:N→ EquipmentFile (CASCADE DELETE)

Archive tables: Archived* (mirror structure, no FK cascade)
User (JWT auth, role-based)
PinnedDocument (shared PDFs, admin upload)
Contract (balance tracking, computed column)
```

**Computed column:**
- `verification_due = (verification_date + interval '1 month' * verification_interval - 1 day)::date`
- Требует `db.flush()` + `db.refresh(equipment)` после insert/update

### API Routes
- `/auth/*` - JWT login, Windows SSO
- `/main-table/*` - CRUD с joined data (verification/responsibility/finance)
- `/files/*` - Upload/download (Cyrillic support, RFC 5987 headers)
- `/archive/*` - Archive/restore/delete (explicit, no FK cascade)
- `/pinned-documents/*` - Shared PDFs (view all, upload/delete admin-only)
- `/backup/*` - pg_dump backup, Excel export (admin-only)
- `/health/*` - System monitoring, logs (admin-only)
- `/contracts/*` - Contract balance notebook (admin-only)
- `/documents/*` - Label/act generation (DOCX templates, Jinja2)

## Critical Development Patterns

### 1. Status Calculation
- Зависит от `verification_due` (computed) И `verification_state`
- Non-work states (storage/verification/repair/archived) ВСЕГДА перекрывают date-based статусы
- ОБЯЗАТЕЛЬНО: `db.flush()` + `db.refresh(equipment)` перед `calculate_status()`

### 2. Archive Operations
- Процесс: Copy to archive → Explicit delete from main
- NO FK CASCADE на уровне архива - удаление в service layer
- Restore: Copy back → Delete from archive
- `archive_reason` - editable inline в ArchiveTable

### 3. RevoGrid Auto-save
- `@afteredit` → GET `/main-table/{id}/full` → update field → PUT `/main-table/{id}`
- Всегда отправлять ПОЛНЫЕ данные (complete equipment object)
- Range editing через `@beforerangeedit`

### 4. File Management
- Cyrillic filenames: RFC 5987 Content-Disposition headers
- Validation: PDF/DOC/DOCX/XLS/XLSX/JPG/PNG, 50 MB limit
- Storage: `backend/uploads/equipment_{id}/`
- Path traversal protection, filename sanitization

### 5. Metrics Dashboard
- Client-side calculation from database data
- Admin: все данные. Laborant: только свой отдел (фильтр на loadData)
- "Списано" metric: загружает archive данные с причиной "Извещение о непригодности"

### 6. Table Display Labels
- cellTemplate для enum: state_work → "В работе", SI → "СИ", lbr → "ЛБР"
- Одинаковые mappings в MainTable, EquipmentModal, FilterPanel

### 7. Document Generation
- docxtpl (Jinja2) + DOCX templates в `docs/docx-templates/`
- Template variables: equipment fields + verification + responsibility
- Table border preservation, automatic row numbering
- RFC 5987 headers для Cyrillic filenames

### 8. First-Run Configuration (Electron)
- **ConfigModal.vue**: Диалог для ввода IP сервера при первом запуске
- **IPC Methods** (preload.js):
  - `window.electron.getConfig()` - чтение из userData/config.json
  - `window.electron.saveConfig(config)` - сохранение конфигурации
- **Динамическое обновление API** (config/api.js):
  - `updateApiBaseUrl(newUrl)` - обновляет все endpoints после настройки
  - `createEndpoints(baseUrl)` - фабрика для генерации endpoint URLs
- **App.vue логика**:
  - Проверка конфигурации при onMounted
  - Если config отсутствует → показать ConfigModal
  - После сохранения → обновить API_BASE_URL → продолжить инициализацию
- **Хранение**: `app.getPath('userData')/config.json` (автоматически создается)

### 9. Electron Build Issues
- ❗ **NSIS требует `icon.ico`** (не PNG!) в `frontend/public/`
- ❗ Запуск от администратора для NSIS установщика
- ❗ Очистка кэша: `Remove-Item $env:LOCALAPPDATA\electron-builder\Cache -Recurse -Force`
- ❗ **Vite config:** `base: './'` обязателен для относительных путей в production
  - БЕЗ этого Electron показывает белое окно (абсолютные пути `/assets/*` не работают с `loadFile()`)
- Config: `forceCodeSigning: false`, `signAndEditExecutable: false`
- Portable версия работает без admin прав

## Important Notes

- **Язык**: Русский для документации и UI (нефтегазовая отрасль)
- **Общение**: Всегда отвечать на русском
- **Department/Person mappings**: Frontend only (не DB constraints)
  - 12 departments: lbr→"ЛБР", gtl→"ГТЛ", etc.
  - 19 responsible persons: enazarov→"Назаров Е.", etc.
- **Laborant filtering**: Frontend фильтр по department в MainTable.vue loadData
- **Finance FK naming**: `equipment_model_id` (inconsistent, но работает)

## Known Issues

### Critical (Commercial Deployment)

- **PostgreSQL Permissions на схему public**:
  - При создании БД через `createdb -U deltica_user` пользователь НЕ получает права на схему public
  - Симптомы: `pg_restore: error: нет доступа к схеме public`
  - РЕШЕНИЕ: После createdb выполнить `GRANT ALL ON SCHEMA public TO deltica_user;` от имени postgres
  - См. раздел "Database Initialization (Commercial Build)" для деталей

- **Устаревший database dump**:
  - `deltica_initial.dump` нужно **пересоздавать перед каждым релизом** с актуальными данными
  - ВАЖНО: Дамп содержит всех пользователей, все оборудование и настройки
  - Команда: `pg_dump -h 127.0.0.1 -p 5432 -U postgres -d deltica_db -F c -b -f backend/database_dumps/deltica_initial.dump`
  - Затем скопировать в `dist/Deltica-Server-v1.0.X/database_dumps/`

- **ConfigModal требует ПОЛНЫЙ URL с портом**:
  - При первом запуске клиента вводить: `http://127.0.0.1:8000` (НЕ просто `127.0.0.1`!)
  - Без `:8000` клиент пытается подключиться к порту 80
  - Конфигурация сохраняется в `%APPDATA%\Deltica\config.json`

- **useAuth.js не синхронизирован с api.js**:
  - `useAuth.js` имеет свою переменную API_URL которая НЕ обновляется через updateApiBaseUrl()
  - Это legacy код который загружает config.json из публичной папки (не работает в Electron)
  - TODO: Рефакторинг - использовать единый источник API_URL

### Minor Issues

- `alembic.ini` line 87: hardcoded DB credentials (should use .env)
- Finance FK: `equipment_model_id` вместо `equipment_id`
- `docs/` в `.gitignore` (не в version control)
- No cleanup для orphaned files (если upload failed after save)
- **PowerShell scripts encoding** (build-server.ps1, build-client.ps1):
  - Русский текст отображается некорректно при запуске через bash
  - РЕШЕНИЕ: Запускать напрямую из PowerShell: `.\build-scripts\build-server.ps1`
  - Скрипты РАБОТАЮТ корректно, проблема только в отображении

## Test Users

После `uv run python backend/scripts/seed_users.py`:
- Admin: `admin` / `admin123`
- Laborants: `ivanov`, `petrova`, `sidorov` / `lab123`

## Documentation

**Все руководства в `docs/guides/`:**
- 📋 README.md, INDEX.txt - Навигация
- 🎯 ЧТО_БРАТЬ_НА_ФЛЕШКУ.txt - Deployment шпаргалка
- 📖 DEPLOYMENT_GUIDE.md - Полное руководство
- 📖 BACKUP_RESTORE_GUIDE.md - Backup инструкция
- 📖 RESULTS_SUMMARY.md - Статус установщиков
- 📖 BUILD_INSTRUCTIONS.md - Как собрать установщики
- 📖 data_import_guide.md - Импорт из Excel

**Root level:**
- INSTALL_GUIDE.txt - Server installation with init-database.bat
- build-scripts/README.md - Commercial build docs

**Commercial Build (dist/):**
- Deltica-Server-v1.0.X-FULL.zip - Сервер с БД и автоинициализацией
- Deltica-Client-v1.0.0-NEW.zip - Клиент с диалогом настройки
- ЧТО_КОПИРОВАТЬ_НА_ФЛЕШКУ.txt - Инструкция для deployment
- INSTALL_GUIDE.txt - Пошаговая установка

## Commercial Deployment Process

### Подготовка релиза на флешку:

1. **Создать АКТУАЛЬНЫЙ дамп БД** (КРИТИЧНО!):
   ```powershell
   # ВАЖНО: Делать ЭТО КАЖДЫЙ РАЗ перед релизом!
   # Дамп содержит всех пользователей, оборудование, настройки

   cd C:\Projects\deltica

   # Создать свежий дамп текущей dev БД
   & "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" `
     -h 127.0.0.1 -p 5432 -U postgres -d deltica_db `
     -F c -b -f backend/database_dumps/deltica_initial.dump

   # Скопировать в dist
   Copy-Item backend/database_dumps/deltica_initial.dump `
             -Destination dist/Deltica-Server-v1.0.1/database_dumps/ -Force

   # Проверить размер файла (должен быть > 100KB если есть данные)
   ls -lh backend/database_dumps/deltica_initial.dump
   ```

2. **Сборка сервера** (с автоинициализацией БД):
   ```bash
   # Пересобрать сервер (⚠️ build-server.ps1 имеет проблемы с кодировкой)
   .\build-scripts\build-server.ps1

   # Проверить что в dist/Deltica-Server-v1.0.X/ есть:
   # - database_dumps/deltica_initial.dump (АКТУАЛЬНЫЙ!)
   # - init-database.bat
   # - INSTALL_GUIDE.txt
   ```

3. **Сборка клиента** (с диалогом настройки):
   ```bash
   cd frontend
   npm run build
   npm run electron:build:win  # Требует admin прав

   # Результат: dist-electron/*.exe (Setup + Portable)
   ```

4. **Упаковка для флешки**:
   - `dist/Deltica-Server-v1.0.X-FULL.zip` (75 MB)
   - `dist/Deltica-Client-v1.0.0-NEW.zip` (203 MB)
   - `dist/INSTALL_GUIDE.txt` (9.5 KB)
   - `dist/ЧТО_КОПИРОВАТЬ_НА_ФЛЕШКУ.txt` (инструкция)

**Чеклист перед релизом:**
- ✅ Создан свежий дамп БД с актуальными данными?
- ✅ Дамп скопирован в dist/Deltica-Server-v1.0.X/database_dumps/?
- ✅ Проверен размер дампа (должен быть >100KB)?
- ✅ В дампе есть пользователи (особенно admin)?
- ✅ Протестирована установка на чистой системе?

### Процесс установки на тестовом ПК:

1. **Установить PostgreSQL 16/17** → создать пользователя `deltica_user` с правами createdb

2. **Распаковать сервер** → настроить `.env`:
   ```env
   DB_HOST=127.0.0.1          # ВАЖНО: Не localhost!
   DB_PORT=5432
   DB_USER=deltica_user
   DB_PASSWORD=deltica123
   DB_NAME=deltica_db
   ```

3. **Запустить `init-database.bat`** (один раз!):
   - Если появится ошибка "нет доступа к схеме public":
     1. Открыть pgAdmin → Query Tool на `deltica_db`
     2. Выполнить:
        ```sql
        GRANT ALL ON SCHEMA public TO deltica_user;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO deltica_user;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO deltica_user;
        ALTER DATABASE deltica_db OWNER TO deltica_user;
        ```
     3. Перезапустить `init-database.bat`

4. **Запустить `start.bat`** → сервер на http://localhost:8000
   - Проверить в браузере: http://localhost:8000/docs (должен открыться Swagger)

5. **Установить клиент** → Deltica-Setup-1.0.0.exe

6. **При первом запуске** → диалог ConfigModal появится автоматически:
   - ⚠️ **ВАЖНО**: Вводить ПОЛНЫЙ URL с портом!
   - Если сервер на том же ПК: `http://127.0.0.1:8000`
   - Если сервер в локальной сети: `http://192.168.X.X:8000`
   - НЕ вводить просто IP без порта - будет ошибка соединения!
   - Конфигурация сохранится в `%APPDATA%\Deltica\config.json`

7. **Войти**: `admin` / `admin123`

**Troubleshooting:**
- Если вход не выполняется - проверить что сервер запущен и доступен
- Если "ошибка соединения" - проверить config.json, убедиться что указан порт `:8000`
- После изменения config.json - перезапустить клиент

### Ключевые преимущества:

✅ **Полная автоматизация БД** - не требует миграций, seed scripts, или ручного SQL
✅ **Автоматическая настройка клиента** - диалог при первом запуске вместо редактирования конфигов
✅ **Автономность** - не требует интернета, Git, Python, Node.js на целевой системе
✅ **Portable версия** - работает без прав администратора

## Repository

- **GitHub**: https://github.com/NazarovEvgn/deltica
- **Owner**: NazarovEvgn
- **Main Branch**: `main`
