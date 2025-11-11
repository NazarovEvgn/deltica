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
- Client: electron-builder → `Deltica-Setup-1.0.0.exe`
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
```

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
│   ├── components/       # Vue SFC (MainTable, EquipmentModal, FilterPanel, etc.)
│   ├── composables/      # useAuth, useEquipmentMetrics, useEquipmentFilters
│   ├── assets/styles/    # fonts.css, colors.css, global.css
│   ├── App.vue           # Root with NConfigProvider theme
│   └── main.js           # Entry, axios config
├── electron/             # main.js, preload.js (ES modules)
├── public/               # favicon.png, icon.ico, fonts/
├── package.json          # build config in "build" section
└── vite.config.js
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

### 8. Electron Build Issues
- ❗ **NSIS требует `icon.ico`** (не PNG!) в `frontend/public/`
- ❗ Запуск от администратора для NSIS установщика
- ❗ Очистка кэша: `Remove-Item $env:LOCALAPPDATA\electron-builder\Cache -Recurse -Force`
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

- `alembic.ini` line 87: hardcoded DB credentials (should use .env)
- Finance FK: `equipment_model_id` вместо `equipment_id`
- `docs/` в `.gitignore` (не в version control)
- No cleanup для orphaned files (если upload failed after save)

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
- INSTALL_GUIDE.txt - Server installation
- build-scripts/README.md - Commercial build docs

## Repository

- **GitHub**: https://github.com/NazarovEvgn/deltica
- **Owner**: NazarovEvgn
- **Main Branch**: `main`
