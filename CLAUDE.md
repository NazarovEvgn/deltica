# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

```bash
# Development
uv run uvicorn backend.core.main:app --reload     # Backend: http://localhost:8000
cd frontend && npm run dev                         # Frontend: http://localhost:5173
cd frontend && npm run electron:dev                # Desktop mode

# Testing
uv run pytest                                      # All 152 tests
uv run pytest backend/tests/test_file.py -v       # Single test file

# Database
uv run alembic upgrade head                        # Apply migrations
uv run python backend/scripts/seed_users.py       # Create admin/admin123
```

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

**⚠️ КРИТИЧНО: Перед сборкой сервера обязательно очистить backend/uploads/**

```bash
# 1. ОЧИСТИТЬ backend/uploads/ (ОБЯЗАТЕЛЬНО!)
# PyInstaller упаковывает все файлы из backend/uploads/ в .exe
# Файлы с длинными именами вызовут ошибку при извлечении:
# "Failed to extract backend\uploads\equipment_1\aaaa...pdf: failed to open target file!"
rm -rf backend/uploads/equipment_*
rm -rf backend/uploads/pinned_documents
# Оставить только .gitkeep

# 2. Server build (PyInstaller) - ВАРИАНТ 1
.\build-scripts\build-server.ps1
# → dist/Deltica-Server-v1.0.X.zip
# ВАЖНО: Запускать из PowerShell, не из bash/IDE
# Создает готовый .env файл с production credentials (DB_HOST=10.190.168.78)

# Server build - ВАРИАНТ 2 (рекомендуется если проблемы с кодировкой)
uv run python build_server_simple.py
# → dist/Deltica-Server-v1.0.1/
# Преимущества: нет проблем с Unicode, работает из любой среды
# Создает готовый .env файл с production credentials (DB_HOST=10.190.168.78)

# 3. Client build (electron-builder, требует admin)
.\build-scripts\build-client.ps1
# → dist/Deltica-Client-v1.0.0.zip

# Результат:
# dist/Deltica-Server-v1.0.X/ - сервер для установки (с готовым .env)
# dist/Deltica-Client-v1.0.0/ - установщики + README
```

### Windows Service (Production Server)
```bash
# Для запуска сервера как службы Windows на рабочем сервере:

# 1. Скачать NSSM (Non-Sucking Service Manager)
# Ссылка: https://nssm.cc/download
# Копировать nssm.exe (из папки win64) в директорию с deltica-server.exe

# 2. Установка службы (от администратора)
.\install-service.bat
# Создает службу DelticaServer с автозапуском

# 3. Запуск службы (от администратора)
.\start-service.bat
# или: net start DelticaServer

# 4. Остановка службы (от администратора)
.\stop-service.bat
# или: net stop DelticaServer

# 5. Удаление службы (от администратора)
.\uninstall-service.bat

# Проверка статуса
sc query DelticaServer

# Логи службы (создаются автоматически)
logs\service-output.log  # Стандартный вывод
logs\service-error.log   # Ошибки

# ВАЖНО:
# - Служба запускается автоматически при старте Windows
# - Автоматический перезапуск при падении (задержка 5 сек)
# - Требуются права администратора для установки/управления
# - См. SERVICE_INSTALL_GUIDE.txt для подробной инструкции
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

**ВАЖНО: DB_HOST должен быть 127.0.0.1**

В `.env` файле ОБЯЗАТЕЛЬНО использовать `DB_HOST=127.0.0.1`, а НЕ `localhost`!
- Причина: На некоторых Windows системах `localhost` не резолвится правильно (проблемы IPv6/IPv4)
- `127.0.0.1` гарантированно работает как IPv4 loopback адрес
- Это критично для init-database.bat и работы сервера

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

**Альтернативные методы инициализации (v2.0):**

Если init-database.bat не работает, использовать файлы из `dist/Database-Init-v2.0/`:

1. **Метод 1: Полная инициализация через SQL** (если БД пустая)
   - Открыть pgAdmin → Query Tool на `deltica_db`
   - Загрузить `create_tables_only.sql`
   - Выполнить (F5)
   - Создаст ВСЕ таблицы включая users (без данных)

2. **Метод 2: Частичная инициализация** (если users уже создана)
   - Открыть pgAdmin → Query Tool на `deltica_db`
   - Загрузить `create_tables_NO_USERS.sql`
   - Выполнить (F5)
   - Создаст все таблицы КРОМЕ users

3. **Метод 3: Восстановление с данными**
   - Использовать `deltica_initial.sql` (plain SQL) вместо `.dump`
   - Загрузить в Query Tool и выполнить
   - Восстановит структуру И данные

См. `БЫСТРАЯ_ИНСТРУКЦИЯ.txt` и `MANUAL_RESTORE_GUIDE.txt` для деталей.

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
**ConfigModal.vue**: Диалог для ввода IP сервера при первом запуске
- Автоматически добавляет `http://` если протокол не указан
- Автоматически добавляет `:8000` если порт не указан
- Пример: `192.168.1.10` → `http://192.168.1.10:8000`

**IPC Methods** (preload.js):
- `window.electron.getConfig()` - чтение из userData/config.json
- `window.electron.saveConfig(config)` - сохранение конфигурации
- `window.electron.getWindowsUsername()` - получение текущего Windows username

**Динамическое обновление API** (config/api.js):
- ❗ **КРИТИЧНО**: ВСЕ компоненты ДОЛЖНЫ использовать `API_ENDPOINTS`, НЕ хардкоженные URL
- `updateApiBaseUrl(newUrl)` - обновляет все endpoints после настройки
- `createEndpoints(baseUrl)` - фабрика для генерации endpoint URLs
- `getApiBaseUrl()` - асинхронное получение URL из конфигурации
- **Доступные endpoints**: mainTable, files, archive, pinnedDocuments, contracts, backup, health, auth, documents

**App.vue логика**:
- Проверка конфигурации при onMounted
- Если config отсутствует → показать ConfigModal
- После сохранения → обновить API_BASE_URL → продолжить инициализацию

**Хранение**: `app.getPath('userData')/config.json`
- Windows: `C:\Users\{user}\AppData\Roaming\Deltica\config.json`

### 9. Windows SSO Authentication
**Как работает**:
1. При запуске Electron вызывается `tryAutoLogin()` из useAuth.js
2. Клиент получает Windows username через `window.electron.getWindowsUsername()`
3. Отправляет POST `/auth/windows-login` с заголовком `X-Windows-Username`
4. Backend ищет пользователя по `windows_username` в БД
5. Возвращает JWT токен для найденного пользователя

**КРИТИЧНО**:
- Клиент ОБЯЗАН отправлять заголовок `X-Windows-Username` с текущим Windows username
- БЕЗ заголовка backend использует `os.environ.get('USERNAME')` - это username **на сервере**, не на клиенте!
- Каждый пользователь входит под своим Windows логином из `users_config.yaml`

**Код в useAuth.js**:
```javascript
const headers = {}
if (window.electron && window.electron.getWindowsUsername) {
  const windowsUsername = window.electron.getWindowsUsername()
  headers['X-Windows-Username'] = windowsUsername
}
const response = await axios.post(`${apiUrl}/auth/windows-login`, {}, { headers })
```

### 10. API Endpoints Configuration
**КРИТИЧНО**: Все HTTP запросы ДОЛЖНЫ использовать `API_ENDPOINTS` из `config/api.js`

**НЕПРАВИЛЬНО**:
```javascript
await axios.get('http://localhost:8000/main-table/')  // ❌ Хардкоженный URL
await axios.get(`http://localhost:8000/files/${id}`)  // ❌ Не работает с удаленным сервером
```

**ПРАВИЛЬНО**:
```javascript
import { API_ENDPOINTS } from '../config/api.js'

await axios.get(API_ENDPOINTS.mainTable)              // ✅ Динамический URL
await axios.get(API_ENDPOINTS.files(equipmentId))     // ✅ Работает с любым сервером
await axios.post(API_ENDPOINTS.documentLabels, data)  // ✅ Правильно
```

**Все endpoints в api.js**:
- Main table: `mainTable`, `mainTableFull(id)`
- Files: `files(equipmentId)`, `fileUpload(equipmentId)`, `fileView(id)`, `fileDownload(id)`, `fileDelete(id)`
- Archive: `archive`, `archiveRestore(id)`, `archiveDelete(id)`, `archiveEquipment(id)`
- Documents: `pinnedDocuments`, `pinnedDocumentUpload`, `pinnedDocumentView(id)`, `pinnedDocumentDownload(id)`, `pinnedDocumentDelete(id)`
- Documents generation: `documentLabels`, `documentConservationAct`, `documentBidPoverka`, `documentBidCalibrovka`, `documentRequest`, `documentCommissioningTemplate`
- Contracts: `contracts`, `contractById(id)`
- Backup: `backupHistory(limit)`, `backupCreate`, `backupExportExcel`
- Health: `healthSystem`, `healthLogs(limit)`
- Auth: `auth`, `login`, `me`

### 11. Electron Build Issues
- ❗ **NSIS требует `icon.ico`** (не PNG!) в `frontend/public/`
- ❗ Запуск от администратора для NSIS установщика
- ❗ Очистка кэша: `Remove-Item $env:LOCALAPPDATA\electron-builder\Cache -Recurse -Force`
- ❗ **Vite config:** `base: './'` обязателен для относительных путей в production
  - БЕЗ этого Electron показывает белое окно (абсолютные пути `/assets/*` не работают с `loadFile()`)
- Config: `forceCodeSigning: false`, `signAndEditExecutable: false`
- Portable версия работает без admin прав

### 12. Windows Service Setup (Production Server)
**Назначение**: Запуск Deltica Server как службы Windows для рабочих серверов

**Инструмент**: NSSM (Non-Sucking Service Manager) - https://nssm.cc/download

**Установка**:
1. Скачать NSSM и скопировать `nssm.exe` (из папки win64) в директорию с `deltica-server.exe`
2. Запустить `install-service.bat` **от администратора**
3. Служба создается с именем `DelticaServer` и настраивается на автозапуск

**Управление службой**:
- Запуск: `start-service.bat` (от администратора) или `net start DelticaServer`
- Остановка: `stop-service.bat` (от администратора) или `net stop DelticaServer`
- Удаление: `uninstall-service.bat` (от администратора)
- Проверка статуса: `sc query DelticaServer`

**Особенности**:
- Автоматический запуск при старте Windows
- Автоматический перезапуск при падении (задержка 5 секунд)
- Логирование в `logs/service-output.log` и `logs/service-error.log`
- Рабочая директория: папка с `deltica-server.exe`
- API доступен на http://localhost:8000

**КРИТИЧНО**:
- Требуются права администратора для всех операций со службой
- Файл `.env` должен быть настроен перед установкой службы
- **DB_HOST должен быть IP адресом** (НЕ localhost!) - используйте 127.0.0.1 для локальной БД или IP сервера для удаленной
- После изменения `.env` или обновления `deltica-server.exe` нужно перезапустить службу

**Troubleshooting**:
- Если служба не запускается → проверить `logs/service-error.log`
- Если база не подключается → проверить PostgreSQL запущен, и `.env` содержит правильный IP адрес в DB_HOST
- Если порт 8000 занят → изменить порт в коде или освободить порт
- Подробная инструкция: `SERVICE_INSTALL_GUIDE.txt`

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

- ⚠️ **PyInstaller упаковывает backend/uploads/ в .exe** (2025-01-14):
  - ПРОБЛЕМА: Если в `backend/uploads/` есть файлы перед сборкой, PyInstaller упаковывает их в .exe
  - Симптомы: При запуске deltica-server.exe ошибка "Failed to extract backend\uploads\equipment_1\aaaa...pdf: failed to open target file!"
  - ПРИЧИНА: Файлы с очень длинными именами превышают ограничения Windows на длину пути (260 символов)
  - **РЕШЕНИЕ**: ОБЯЗАТЕЛЬНО очищать `backend/uploads/` перед каждой сборкой:
    ```bash
    rm -rf backend/uploads/equipment_*
    rm -rf backend/uploads/pinned_documents
    # Оставить только .gitkeep
    ```
  - Build-скрипты автоматически создают пустую папку `uploads/` в release, но НЕ очищают исходную папку
  - При переносе старых файлов в production - копировать вручную ПОСЛЕ установки сервера

- **Критические файлы отсутствуют в сборке**:
  - PyInstaller упаковывает все data files ВНУТРЬ .exe, но некоторые скрипты ищут их рядом с .exe
  - Симптомы: "Checking tables...Tables not found. Failed to restore database from dump!", отсутствуют config/, docs/, migrations/, alembic.ini
  - ПРОБЛЕМА: В старых версиях build-server.ps1 не копировались папки после сборки PyInstaller
  - РЕШЕНИЕ: build-server.ps1 теперь вручную копирует database_dumps, config, docs, migrations, alembic.ini после сборки
  - **ОБЯЗАТЕЛЬНАЯ проверка перед упаковкой** - `dist/Deltica-Server-v1.0.X/` должна содержать:
    - database_dumps/deltica_initial.dump (>100KB)
    - config/ (users_config.yaml и др.)
    - docs/ (docx-templates/ с шаблонами)
    - migrations/ (alembic миграции)
    - alembic.ini
  - Если файлы отсутствуют - скопировать вручную:
    ```powershell
    Copy-Item ".\config" ".\dist\Deltica-Server-v1.0.1\config" -Recurse -Force
    Copy-Item ".\docs" ".\dist\Deltica-Server-v1.0.1\docs" -Recurse -Force
    Copy-Item ".\migrations" ".\dist\Deltica-Server-v1.0.1\migrations" -Recurse -Force
    Copy-Item ".\alembic.ini" ".\dist\Deltica-Server-v1.0.1\alembic.ini" -Force
    Copy-Item ".\backend\database_dumps\deltica_initial.dump" ".\dist\Deltica-Server-v1.0.1\database_dumps\deltica_initial.dump" -Force
    ```

- **PostgreSQL Permissions на схему public**:
  - При создании БД через `createdb -U deltica_user` пользователь НЕ получает права на схему public
  - Симптомы: `pg_restore: error: нет доступа к схеме public`
  - РЕШЕНИЕ: После createdb выполнить `GRANT ALL ON SCHEMA public TO deltica_user;` от имени postgres
  - См. раздел "Database Initialization (Commercial Build)" для деталей

- **init-database скрипты падают на шаге 3 на рабочем сервере** (2025-11-19):
  - ПРОБЛЕМА: init-database.bat и init-database-IMPROVED.bat не могут восстановить таблицы на некоторых серверах
  - Симптомы: База deltica_db создана, backend запускается, авторизация работает, но функционал не работает (нет таблиц equipment, verification, и т.д.)
  - ПРИЧИНА: Проблемы с правами доступа при pg_restore, или таблица users создана вручную
  - **РЕШЕНИЕ v2.0**: Использовать новые файлы в `dist/Database-Init-v2.0/`:
    - `create_tables_NO_USERS.sql` - создает ВСЕ таблицы кроме users (14 KB, для случая когда users уже создана вручную)
    - `create_tables_only.sql` - создает ВСЕ таблицы включая users (27 KB, полная схема)
    - `deltica_initial.sql` - plain SQL дамп с данными (1.3 MB, альтернатива бинарному дампу)
    - `БЫСТРАЯ_ИНСТРУКЦИЯ.txt` - пошаговая инструкция для восстановления через pgAdmin
  - **Использование**: Открыть pgAdmin → Query Tool → Open File → create_tables_NO_USERS.sql → Execute (F5)
  - Файлы используют `IF NOT EXISTS`, можно запускать несколько раз без ошибок
  - После создания таблиц функционал (добавление оборудования, загрузка документов, архивирование) должен работать полностью

- **Устаревший database dump**:
  - `deltica_initial.dump` нужно **пересоздавать перед каждым релизом** с актуальными данными
  - ВАЖНО: Дамп содержит всех пользователей, все оборудование и настройки
  - Команда: `pg_dump -h 127.0.0.1 -p 5432 -U postgres -d deltica_db -F c -b -f backend/database_dumps/deltica_initial.dump`
  - Затем скопировать в `dist/Deltica-Server-v1.0.X/database_dumps/`

- **Конфигурация сервера в Electron**:
  - ConfigModal автоматически добавляет порт `:8000` если не указан пользователем
  - Конфигурация сохраняется в `%APPDATA%\Deltica\config.json` (НЕ в папке установки!)
  - `useAuth.js` и `api.js` используют единый источник конфигурации через `window.electron.getConfig()`
  - При вводе `192.168.1.10` автоматически преобразуется в `http://192.168.1.10:8000`

### Minor Issues

- `alembic.ini` line 87: hardcoded DB credentials (should use .env)
- Finance FK: `equipment_model_id` вместо `equipment_id`
- `docs/` в `.gitignore` (не в version control)
- No cleanup для orphaned files (если upload failed after save)
- **PowerShell scripts encoding** (build-server.ps1, build-client.ps1):
  - Русский текст отображается некорректно при запуске через bash или из IDE
  - РЕШЕНИЕ 1: Запускать напрямую из PowerShell: `.\build-scripts\build-server.ps1`
  - РЕШЕНИЕ 2: Использовать `build_server_simple.py` (Python скрипт без проблем с кодировкой)
  - Скрипты РАБОТАЮТ корректно, проблема только в отображении Unicode символов

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

**Database Init v2.0 (dist/Database-Init-v2.0/):**
- 🎯 `create_tables_NO_USERS.sql` - Создание таблиц БЕЗ users (для случая когда users создана вручную)
- 📋 `create_tables_only.sql` - Создание ВСЕХ таблиц (полная схема без данных)
- 💾 `deltica_initial.sql` - Plain SQL дамп с данными (1.3 MB, альтернатива .dump)
- 💾 `deltica_initial.dump` - Бинарный дамп PostgreSQL (106 KB)
- 🔧 `init-database.bat` - Улучшенный батник с выбором метода восстановления
- 📖 `БЫСТРАЯ_ИНСТРУКЦИЯ.txt` - Пошаговая инструкция для создания таблиц через pgAdmin
- 📖 `MANUAL_RESTORE_GUIDE.txt` - Детальное руководство по ручному восстановлению БД

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
   # ⚠️ КРИТИЧНО: Очистить backend/uploads/ ПЕРЕД сборкой!
   rm -rf backend/uploads/equipment_*
   rm -rf backend/uploads/pinned_documents
   # Оставить только .gitkeep

   # Пересобрать сервер (⚠️ build-server.ps1 имеет проблемы с кодировкой при выводе)
   .\build-scripts\build-server.ps1
   # Создает готовый .env с production credentials (DB_HOST=10.190.168.78)

   # КРИТИЧНО: Проверить что database_dumps скопирован
   ls .\dist\Deltica-Server-v1.0.X\database_dumps\deltica_initial.dump

   # Если дамп отсутствует - скопировать вручную:
   New-Item -ItemType Directory -Path ".\dist\Deltica-Server-v1.0.1\database_dumps\" -Force
   Copy-Item ".\backend\database_dumps\deltica_initial.dump" ".\dist\Deltica-Server-v1.0.1\database_dumps\deltica_initial.dump"

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
- ✅ **КРИТИЧНО**: Очищена папка backend/uploads/ перед сборкой? (equipment_*, pinned_documents)
- ✅ Создан свежий дамп БД с актуальными данными?
- ✅ **КРИТИЧНО**: Все папки скопированы в dist/Deltica-Server-v1.0.X/? (PyInstaller НЕ копирует автоматически!)
  - database_dumps/deltica_initial.dump (>100KB)
  - config/ (users_config.yaml)
  - docs/ (docx-templates/)
  - migrations/ (alembic)
  - alembic.ini
- ✅ Проверен размер дампа (должен быть >100KB)?
- ✅ В дампе есть пользователи (особенно admin)?
- ✅ В dist есть готовый .env с production credentials (DB_HOST=10.190.168.78)?
- ✅ ZIP архив пересоздан после копирования всех файлов?
- ✅ Протестирована установка на чистой системе?

### Процесс ОБНОВЛЕНИЯ серверной части (если БД уже работает):

1. **Остановить текущий сервер** (закрыть окно start.bat)
2. **Заменить ТОЛЬКО deltica-server.exe** новой версией
3. **НЕ трогать**: .env, uploads/, logs/, backups/, database_dumps/
4. **Запустить start.bat** → проверить http://localhost:8000/docs
5. **НЕ запускать init-database.bat** (БД уже содержит данные)

### Сценарии установки серверной части

Есть два основных сценария установки в зависимости от того, существует ли уже база данных:

---

## СЦЕНАРИЙ A: Подключение к существующей БД (Production)

**Когда использовать**: База данных уже работает на сервере (например, 10.190.168.78), нужно только установить Deltica Server для подключения к ней.

1. **Распаковать сервер** → проверить `.env` (уже готовый!):
   ```env
   # .env уже содержит production credentials:
   DB_HOST=10.190.168.78     # IP рабочего сервера БД
   DB_PORT=5432
   DB_USER=deltica_user
   DB_PASSWORD=deltica123
   DB_NAME=deltica_db
   ```
   ⚠️ `.env` уже настроен с правильным IP - если БД на другом адресе, отредактировать DB_HOST

2. **❌ НЕ ЗАПУСКАТЬ init-database.bat!** (база уже существует и содержит данные)

3. **Запустить `start.bat`** → сервер подключится к существующей БД
   - API: http://localhost:8000
   - Swagger: http://localhost:8000/docs

4. **Установить клиент** → Deltica-Setup-1.0.0.exe

5. **При первом запуске клиента** → ConfigModal появится автоматически:
   - Если сервер на том же ПК: `127.0.0.1` или `localhost`
   - Если сервер в локальной сети: `192.168.X.X`
   - Порт `:8000` добавится автоматически

6. **Войти** используя существующие учетные данные из БД

---

## СЦЕНАРИЙ B: Новая установка с нуля (Fresh Install)

**Когда использовать**: Устанавливаем на новый сервер, база данных НЕ существует, нужно создать все с нуля.

1. **Установить PostgreSQL 16/17** → создать пользователя `deltica_user` с правами createdb

2. **Распаковать сервер** → отредактировать `.env`:
   ```env
   # Для локальной установки:
   DB_HOST=127.0.0.1         # ВАЖНО: 127.0.0.1, НЕ localhost!
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
   - Если сервер на том же ПК: `127.0.0.1` или `localhost`
   - Если сервер в локальной сети: `192.168.X.X`
   - 💡 Порт `:8000` добавится автоматически!
   - Можно указать полный URL: `http://192.168.X.X:8000`
   - Конфигурация сохранится в `%APPDATA%\Deltica\config.json`

7. **Войти**: `admin` / `admin123`

**Troubleshooting:** См. раздел "Known Issues" для решения проблем с init-database.bat и PostgreSQL permissions.

### Ключевые преимущества:

✅ **Полная автоматизация БД** - не требует миграций, seed scripts, или ручного SQL
✅ **Автоматическая настройка клиента** - диалог при первом запуске вместо редактирования конфигов
✅ **Автономность** - не требует интернета, Git, Python, Node.js на целевой системе
✅ **Portable версия** - работает без прав администратора

## Repository

- **GitHub**: https://github.com/NazarovEvgn/deltica
- **Owner**: NazarovEvgn
- **Main Branch**: `main`
