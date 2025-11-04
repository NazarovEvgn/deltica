# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Deltica is a metrology equipment management system for oil & gas companies. It tracks metrology equipment (measuring instruments and testing equipment) and their verification schedules (calibration, verification, certification).

**Key Domain Concepts:**
- **Equipment Types**: 'SI' (measuring instruments / СИ), 'IO' (testing equipment / ИО)
- **Verification**: Periodic procedures (calibration/verification/certification) with validity periods
- **User Roles**: Admin (CRUD operations), Laborant (read-only access to department equipment)
- **Equipment Lifecycle**: States (work/storage/verification/repair/archived) and statuses (fit/expired/expiring)

## Tech Stack

- **Frontend**: Vue.js 3 with Vite (Node.js ^20.19.0 || >=22.12.0)
  - **UI Library**: Naive UI (components: NButton, NSpace, NSelect, NModal, etc.)
  - **Data Grid**: RevoGrid (@revolist/vue3-datagrid) for main table with Excel-like features
  - **HTTP Client**: Axios for API requests
  - **Typography**: PT Astra Sans (Regular, Bold, Italic) - applied globally via NConfigProvider
  - **Branding**: Custom favicon.png in `frontend/public/`, corporate colors from `poster.png`
  - **Corporate Colors**: Gazprom Neft palette defined in `frontend/src/assets/styles/colors.css`
    - Primary Blue: `#0071BC`, Info Blue: `#00A6E4`, Orange: `#F7941D`, Green: `#8BC53F`
- **Backend**: FastAPI with Python 3.13 managed by uv
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Desktop**: Electron (планируется) - нативное Windows приложение с Vite frontend (миграция с Tauri из-за конфликта с RevoGrid)

## Development Commands

### Environment Setup
```bash
# Copy environment template and configure database credentials
cp .env.example .env
# Edit .env with your PostgreSQL credentials (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend && npm install
```

### Quick Start
```bash
# Windows PowerShell (рекомендуется) - запускает backend и frontend одновременно
.\start.ps1

# Windows CMD
start.bat
```

### Backend Development
```bash
# Run FastAPI backend with auto-reload (default port 8000)
uv run uvicorn backend.core.main:app --reload

# Start on different port if needed
uv run uvicorn backend.core.main:app --reload --port 8001

# API documentation: http://localhost:8000/docs (Swagger UI)
```

### Frontend Development
```bash
cd frontend
npm run dev        # Start development server (http://localhost:5173)
npm run build      # Build for production
npm run preview    # Preview production build
```

### Desktop Application (Electron) - ✅ ГОТОВО И РАБОТАЕТ

**Текущий статус:** Electron desktop режим полностью настроен, протестирован и собран. RevoGrid корректно отображается. **Portable ZIP версия готова к распространению!**

**Готовые установщики:**
- ✅ **Portable ZIP** (146 MB): `frontend/dist-electron/Deltica-Portable-1.0.0.zip` - **ГОТОВ К ИСПОЛЬЗОВАНИЮ**
- ✅ **Unpacked версия**: `frontend/dist-electron/win-unpacked/Deltica.exe` - для тестирования
- ⚠️ **NSIS установщик**: требует сборки от имени администратора (см. `BUILD_INSTRUCTIONS.md`)

**Причина миграции с Tauri:**
- Tauri v2 показал проблемы с RevoGrid (отсутствие отображения таблицы из-за кэширования)
- Проблемы с кэшем и рендерингом в WebView2
- Electron гарантирует совместимость через встроенный Chromium

**Архитектура:**
- Electron (main/renderer) + Vite + Vue 3 + Naive UI + RevoGrid
- Backend (FastAPI) остается отдельным процессом на `http://localhost:8000`
- Electron - только frontend обертка (не embedded backend)
- Security: contextIsolation + отключенный nodeIntegration + preload script
- ES modules синтаксис в electron файлах (main.js, preload.js)

**Установленные зависимости:**
- electron ^38.4.0
- electron-builder ^26.0.12 (для Windows установщиков)
- concurrently ^9.2.1 (параллельный запуск Vite + Electron)
- wait-on ^9.0.1 (ожидание готовности Vite dev server)
- cross-env ^10.1.0 (кроссплатформенные переменные окружения)

**Команды запуска:**
```bash
# Вариант 1: Автоматический запуск dev режима (рекомендуется)
.\start-desktop.bat         # или
.\start-desktop.ps1

# Вариант 2: Ручной запуск dev режима
# Терминал 1: Backend
uv run uvicorn backend.core.main:app --reload

# Терминал 2: Electron
cd frontend
npm run electron:dev

# Production сборка Windows установщиков
cd frontend
npm run build              # Сборка production frontend (обязательно!)
npm run electron:build:win # Создаст установщики (требует admin для NSIS)

# Альтернативный способ (с правами администратора)
cd frontend
.\build-installer.ps1      # PowerShell скрипт для автоматической сборки
```

**Критические исправления и улучшения (2025-11-04):**
- **Production build**: Полностью настроена сборка установщиков
- **Portable ZIP**: Готовая portable версия создана и протестирована (146 MB)
- **Иконка приложения**: Создана иконка 256x256 из оригинальной favicon.png (30x35)
- **NSIS конфигурация**: Настроен русский интерфейс установщика, ярлыки, autorun
- **Скрипты сборки**: PowerShell скрипты для автоматизации (`build-installer.ps1`, `create-icon.ps1`)
- **Документация**: Полный набор руководств в `docs/guides/`
- **Автоочистка кэша**: `session.clearCache()` при запуске в dev режиме
- **CORS настройки**: расширен backend CORS для поддержки `null` origin (Electron)
- **webSecurity: false**: отключены CORS проверки для localhost API
- **UTF-8 кодировка**: исправлено отображение русских символов в PowerShell

**Важно:**
- ✅ **Portable ZIP готов к использованию** - не требует дополнительных действий
- Vite dev server зафиксирован на порту 5173 (strictPort: true)
- Кэш автоматически очищается при каждом dev запуске для предотвращения проблем с RevoGrid
- NSIS установщик требует прав администратора для сборки (проблема winCodeSign в Windows)
- При первом запуске PowerShell может потребовать разрешение политики выполнения:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

**Структура установщиков:**
```
frontend/dist-electron/
├── Deltica-Portable-1.0.0.zip  # ✅ ГОТОВ (146 MB) - распространять как есть
├── win-unpacked/               # ✅ ГОТОВ - для тестирования
│   └── Deltica.exe
└── [После admin сборки:]
    ├── Deltica-Setup-1.0.0.exe     # NSIS установщик (~70 MB)
    └── Deltica-Portable-1.0.0.exe  # Portable EXE (~70 MB)
```

### Database Management
```bash
# Check current migration status
uv run alembic current

# View migration history
uv run alembic history

# Create new migrations (when models.py changes)
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations to database
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Testing
```bash
# Run all tests (152 total)
uv run pytest

# Run specific test files
uv run pytest backend/tests/test_file_utils.py       # File utilities (39 tests)
uv run pytest backend/tests/test_files_api.py        # File API (17 tests)
uv run pytest backend/tests/test_files_security.py   # File security (20 tests)
uv run pytest backend/tests/test_files_encoding.py   # File encoding (16 tests)
uv run pytest backend/tests/test_status_calculation.py  # Status calculation (11 tests)
uv run pytest backend/tests/test_verification_due.py    # Verification due (6 tests)
uv run pytest backend/tests/test_archive.py          # Archive functionality (16 tests)
uv run pytest backend/tests/test_pinned_documents.py # Pinned documents API (23 tests)

# Run single test by name
uv run pytest backend/tests/test_files_api.py::test_upload_file_success -v

# Run with coverage report
uv run pytest backend/tests/test_file*.py --cov=backend.routes.files --cov-report=html
```

### User Management
```bash
# Initial user creation (run once for initial setup)
uv run python backend/scripts/seed_users.py
# Creates admin user (admin/admin123) and laborant users from responsibility table (password: lab123)

# Sync users from YAML config (run after editing config/users_config.yaml)
uv run python backend/scripts/sync_users.py
# Reads config/users_config.yaml and creates/updates users
```

## Architecture

### Backend Structure
```
backend/
├── core/           # Application core (config, database, main)
│   ├── config.py       # Environment config via pydantic-settings
│   ├── database.py     # SQLAlchemy engine, session, get_db() dependency
│   └── main.py         # FastAPI app instance with routers
├── app/            # Domain models and schemas
│   ├── models.py       # SQLAlchemy ORM models (Equipment, Verification, User, etc.)
│   └── schemas.py      # Pydantic schemas for API requests/responses
├── services/       # Business logic layer
│   ├── main_table.py   # MainTableService with CRUD logic
│   └── archive.py      # ArchiveService with archive/restore/delete logic
├── routes/         # API endpoints (/main-table, /files, /archive, /auth, /pinned-documents)
├── utils/          # Utility functions (auth helpers)
├── scripts/        # Management scripts (seed_users.py, sync_users.py)
└── tests/          # Test suite (152 tests total, all passing)
```

### Database Schema Overview

**Core entities:**
- **Equipment** → **Verification** (one-to-many)
- **Equipment** → **Responsibility** (one-to-one, via equipment_id FK)
- **Equipment** → **Finance** (one-to-one, via equipment_model_id FK) ⚠️ Note: inconsistent FK naming
  - **Finance fields**: budget_item (NOT NULL), code_rate, cost_rate, quantity, coefficient, total_cost, invoice_number, paid_amount, payment_date
  - **total_cost**: Auto-calculated on frontend (cost_rate * quantity * coefficient)
- **Equipment** → **EquipmentFile** (one-to-many, CASCADE DELETE)

**Archive entities:** Mirror structure of main tables (ArchivedEquipment, ArchivedVerification, ArchivedResponsibility, ArchivedFinance, ArchivedEquipmentFile)

**Authentication:** User table with role-based access (admin/laborant), managed via YAML config (config/users_config.yaml)

**Pinned Documents:** PinnedDocument table for shared PDF files (instructions, schedules, etc.) accessible to all users. Admin-only upload/delete. Storage: `backend/uploads/pinned_documents/`

**Important computed column:**
- `verification_due` is a PostgreSQL computed column: `(verification_date + interval '1 month' * verification_interval - interval '1 day')::date`
- Requires `db.flush()` and `db.refresh(equipment)` to retrieve computed value after insert/update

### API Routes

All routes documented in Swagger UI at `http://localhost:8000/docs`

**Key endpoints:**
- `/main-table/*` - CRUD operations for equipment with joined verification/responsibility/finance data
- `/files/*` - File upload/download/view with Cyrillic support (RFC 5987 headers)
- `/archive/*` - Archive/restore/delete with explicit deletion (no FK CASCADE)
- `/auth/*` - JWT authentication (24-hour expiration), bcrypt password hashing
- `/pinned-documents/*` - Shared PDF documents (view/download for all, upload/delete admin-only)
- `/backup/*` - Database backup operations (admin-only, uses pg_dump)
- `/health/*` - System monitoring and health checks (admin-only)
- `/contracts/*` - Contract balance notebook (admin-only)
- `/documents/*` - Label generation for equipment (single and batch, DOCX templates with Jinja2)

### Critical Development Patterns

**1. Status Calculation Logic** (`backend/services/main_table.py::calculate_status()`):
- Status depends on BOTH `verification_due` (computed column) and `verification_state`
- Non-work states (storage/verification/repair/archived) ALWAYS override date-based statuses
- Must call `db.flush()` and `db.refresh(equipment)` before calculating status to get computed `verification_due`

**2. Archive Operations** (`backend/services/archive.py`):
- Archive process: Copy to archive tables → Explicitly delete from main tables
- NO FK CASCADE on archive level - deletion is explicit in service layer
- Restore process: Copy back to main tables → Delete from archive tables
- **Editable archive_reason column**: Users can edit "Причина списания" inline in ArchiveTable via RevoGrid `@afteredit` event
  - PATCH endpoint: `/archive/{archived_equipment_id}/reason`
  - Updates ArchivedEquipment.archive_reason field
  - Auto-saves on cell edit with error handling and data reload on failure

**3. File Management** (`backend/routes/files.py`):
- Full Cyrillic filename support with RFC 5987 Content-Disposition headers
- File type validation (PDF, DOC, DOCX, XLS, XLSX, JPG, PNG), 50 MB size limit
- Path traversal protection and filename sanitization
- Storage: filesystem at `backend/uploads/equipment_{id}/`

**4. RevoGrid Auto-save Pattern** (`frontend/src/components/MainTable.vue`):
- Cell edit triggers `@afteredit` event
- Calls `GET /main-table/{id}/full` to get complete equipment data
- Updates changed field in received data
- Sends `PUT /main-table/{id}` with complete updated data
- Range editing (drag-to-fill, Ctrl+C/Ctrl+V) uses `@beforerangeedit` event

**5. Database Session Management**:
- Use dependency injection via `get_db()` in routes
- Service layer handles business logic, routes handle HTTP concerns
- Full entity CRUD: Service methods create/update/delete across all related tables
- Main table queries use LEFT OUTER JOIN to include equipment without verification/responsibility/finance
- **Finance data**: Included in main table response via LEFT JOIN (backend/services/main_table.py)

**6. Authentication Flow**:
- JWT tokens stored in localStorage
- Axios interceptors automatically add Bearer token to requests
- Role-based UI: Components check `isAdmin`/`isLaborant` computed properties
- User management via YAML config (config/users_config.yaml), not database admin panel

**7. Pinned Documents** (`backend/routes/pinned_documents.py`, `frontend/src/components/DocumentsPanel.vue`):
- PDF-only validation (50 MB limit), filename sanitization (supports Cyrillic)
- Admin-only upload/delete (via `get_current_active_admin` dependency)
- All authenticated users can view/download (via `get_current_user` dependency)
- File viewing uses axios with blob + JWT authentication (not direct file URLs)
- Storage: `backend/uploads/pinned_documents/` with unique filename generation
- Frontend: Button in top-right of MainTable, opens Naive UI modal with file list

**8. Metrics Dashboard** (`frontend/src/composables/useEquipmentMetrics.js`, `frontend/src/components/MetricsDashboard.vue`):
- Client-side metrics calculation from database data (not filtered data)
- Displays 7 key metrics: total, fit, expired, on verification, in storage, in repair, **failed (списано)**
- For admin: metrics show statistics for entire database
- For laborant: metrics show statistics only for their department (filtered at loadData level)
- **Failed metric**: Counts equipment archived with reason "Извещение о непригодности" from archive table
  - Loads archive data on component mount via `GET /archive/`
  - Filters by department for laborants, shows all for admins
- Metrics are reactive and update automatically when data is reloaded
- Location: Between action buttons and search bar in MainTable
- Compact card design with monochrome styling (#333) and hover effects

**9. Database Backup** (`backend/routes/backup.py`, `backend/services/backup.py`, `frontend/src/components/BackupPanel.vue`):
- Admin-only functionality using pg_dump for PostgreSQL backups
- Auto-detects PostgreSQL installation (supports versions 13-17 on Windows)
- Backups stored in `backend/backups/` with timestamp naming
- History tracking in `backup_history` table (file name, size, status, creator)
- Frontend: Simple log-style interface showing backup history
- No frequency limitations - admin can create backups on demand
- Location: Button in admin panel next to Archive button
- **Excel Export**: Additional button to export all database data to Excel (.xlsx) format
  - Exports all equipment data with joined verification/responsibility/finance tables
  - Russian column headers with auto-sized columns
  - File naming: `deltica_export_YYYYMMDD_HHMMSS.xlsx`
  - Uses pandas + openpyxl for Excel generation
  - Direct download with RFC 5987 headers for Cyrillic filenames

**10. Logging and Monitoring** (`backend/core/logging_config.py`, `backend/middleware/logging_middleware.py`, `backend/routes/health.py`, `frontend/src/components/SystemMonitor.vue`):
- **Structured JSON logging** with automatic rotation (daily, 30-day retention)
- **LoggingMiddleware**: Auto-logs all HTTP requests (method, path, status, duration, user, IP)
- **Event logging**: Auth events (login success/failure), CRUD operations, backup operations
- **Health endpoints**: `/health/` (public), `/health/system` (admin - system metrics), `/health/logs` (admin - log viewing)
- **SystemMonitor component**: Two-tab interface (System Status + Logs)
  - System Status: DB connection, CPU/memory/disk usage, log file statistics
  - Logs: Last 100 entries with JSON parsing, color-coded by level (INFO/WARNING/ERROR)
- **Log storage**: `backend/logs/deltica.log` (JSON format, UTF-8)
- **Dependencies**: psutil for system metrics
- Location: "Мониторинг" button in admin panel next to Backup button

**11. Typography and Branding** (`frontend/public/fonts/`, `frontend/src/assets/styles/`):
- **Font**: PT Astra Sans (Regular 400, Bold 700, Italic 400) - TTF format
- **Font loading**: `@font-face` declarations in `frontend/src/assets/styles/fonts.css`
- **Global application**: Applied via `NConfigProvider` themeOverrides in `App.vue`
- **RevoGrid tables**: Font explicitly set in MainTable.vue and ArchiveTable.vue styles
- **Favicon**: Custom PNG favicon in `frontend/public/favicon.png`
- **Styling structure**:
  - `frontend/src/assets/styles/fonts.css` - Font declarations
  - `frontend/src/assets/styles/global.css` - Global styles (body, #app, reset)
  - `frontend/src/assets/styles/colors.css` - Corporate color constants
  - Imported in `frontend/src/main.js`

**12. Data Import from Excel** (`backend/scripts/import_equipment_data.py`, `docs/data_import_guide.md`):
- **Purpose**: Import equipment data from Excel files into PostgreSQL database
- **Value Mappings**: Russian → English enum conversion (поверка→verification, ЛБР→lbr, СИ→SI)
- **NULL Handling**: Default values for required fields (equipment_year: 2000, quantity: 1, etc.)
- **Date Processing**: Auto-fix malformed dates, calculate verification_plan from date + interval
- **Department Mapping**: Critical for user filtering - Russian labels converted to technical values
- **Scripts**:
  - `import_equipment_data.py` - reads Excel, generates SQL with value mapping
  - `execute_import_sql.py` - executes SQL via SQLAlchemy with transaction safety
- **Documentation**: `docs/data_import_guide.md` contains comprehensive import guide with all mappings and troubleshooting

**13. Table Display Labels** (`frontend/src/components/MainTable.vue`):
- **cellTemplate Pattern**: Custom rendering for enum columns to display Russian labels instead of technical values
- **Mapped Columns**:
  - `verification_state`: state_work → "В работе", state_storage → "На консервации"
  - `verification_type`: verification → "Поверка", calibration → "Калибровка"
  - `equipment_type`: SI → "СИ", IO → "ИО"
  - `department`: lbr → "ЛБР", gtl → "ГТЛ" (12 departments total)
  - `status`: Already has color-coded mapping
- **Implementation**: Each mapped column uses `cellTemplate` with createElement to render custom span with display text
- **Consistency**: Same mappings used across MainTable, EquipmentModal, FilterPanel, and composables

**14. UI/UX Design Guidelines** (implemented from `docs/deltica_dev_plan.md`):
- **Layout Structure**:
  - Row 1: AppLogo (left) → MetricsDashboard (center) → UserProfile (right)
  - Row 2: Buttons (left: Filters, Documents, Statistics, Admin Panel) → SearchBar (center, 600px) → Empty spacer (right)
  - CSS Grid layout (1fr auto 1fr) ensures true centering regardless of side content
  - Main table below with white background on light gray (#f5f5f5) page
- **AppLogo Component**: 24x24px favicon + "Deltica" text (black #333, bold), 6px gap, clickable (returns to main/scrolls to top)
- **Metrics Dashboard**: Monochrome design (#333), no colored indicators, increased font sizes (value: 17px, label: 11px)
- **User Profile Display**: Format "Department Surname I." with icon at right, no role tag, dropdown menu contains only "Logout"
- **Admin Panel Component** (`AdminPanel.vue`):
  - NDropdown with hover trigger, Primary button style
  - Menu items: "Добавить оборудование", "Архив", "Backup БД", "Мониторинг"
  - Consolidates all admin actions in one place
  - BackupPanel and SystemMonitor components have buttons removed, controlled via refs and `openModal()` method
- **Button Styles**:
  - All action buttons use `type="primary"` (Filters, Documents, Statistics, Admin Panel)
  - Border radius: 6px (unified with tables and inputs)
  - Table action buttons (Edit/Delete/View): gray (#8c8c8c)
- **Documents & Statistics Buttons**: Positioned in button row (row 2), both `type="primary"`
- **Documents Modal**: Title "Документы по метрологическому обеспечению в филиале", displays date only (no time/author)
- **Equipment View Modal**:
  - Title: "Полная информация по оборудованию и закрепленные файлы"
  - Section names: "Оборудование", "Верификация", "Ответственные лица", "Финансы"
  - Finance section visible only for admins (`v-if="isAdmin"`) in both read-only and edit modes
  - Finance field labels: "Статья бюджета" (required), "Тариф", "Стоимость по тарифу (без НДС)", "Кол-во", "Доп. коэффициент", "Итоговая стоимость (без НДС)" (auto-calculated, disabled), "Номер счета", "Факт оплаты", "Дата оплаты"
  - Disabled fields: white background with black text (no gray) for readability
- **Border Radius**: Unified 6px for all elements (buttons, inputs, tables via `App.vue` themeOverrides)
- **Corporate Colors**: Applied throughout via `App.vue` themeOverrides and individual components
  - All action buttons: Primary Blue (#0071BC)
  - Table action buttons: Corporate gray (#8c8c8c)
  - Document links: Primary Blue (#0071BC)
  - Section dividers: Primary Blue (#0071BC)
- **Background**: Light gray (#f5f5f5) for body, white (#ffffff) for tables
- **RevoGrid Table Features**:
  - Sorting: `sortable: true` on all data columns, click header to sort ascending/descending
  - Filtering: `filter: 'string'` on all data columns, conditional filters (contains, begins, eq, etc.)
  - Filter plugin enabled with `:filter="true"` on v-grid component
  - Both sort and filter icons visible on hover (opacity: 0.3 by default, 1.0 on hover or when active)
  - Column resizing enabled with `:resize="true"`

**15. Document Generation (Labels and Acts)** (`backend/routes/documents.py`, `backend/services/documents.py`):
- **Purpose**: Generate equipment labels and conservation acts from DOCX templates using docxtpl (Jinja2 templating)
- **Templates**: Stored in `docs/docx-templates/`
- **Output**: Generated documents in `backend/generated_documents/`
- **Features**:
  - Single label generation: `GET /documents/label/{equipment_id}`
  - Batch label generation: `POST /documents/labels` with array of equipment_ids
  - Conservation act generation: `POST /documents/conservation-act` with array of equipment_ids
  - Table border preservation in generated documents (critical for layout)
  - Automatic row numbering with proper formatting (1., 2., 3., etc.)
  - Full equipment data context (equipment + verification + responsibility)
  - Department mapping for display (technical values → Russian labels)
- **Templates**:
  - `template_label.docx` - Equipment labels (single table cell format)
  - `template_storage.docx` - Conservation act (multi-row table with automatic numbering)
- **Template Variables**: Available in context
  - Equipment fields: equipment_name, equipment_model, equipment_specs, factory_number, inventory_number, etc.
  - Verification fields: verification_type, verification_date, registry_number, verification_due, etc.
  - Responsibility fields: department (mapped to Russian), responsible_person, verifier_org
- **RFC 5987 headers**: Cyrillic filenames (e.g., "Этикетка_{id}.docx", "Акт_консервации_{count}_шт.docx")
- **Access**: All authenticated users can generate documents
- **Frontend**: DocumentActionsDropdown component with hover menu ("Печать этикетки", "Акт консервации")
- **Recent fixes** (2025-10-25):
  - Table border preservation when generating labels from templates
  - Conservation act generation with automatic row numbering and point formatting

**16. Laborant Statistics** (`frontend/src/components/LaborantStatistics.vue`):
- **Purpose**: Verification statistics dashboard for laborants with date range filtering
- **Features**:
  - Date range selector (default: current year, Jan 1 - Dec 31)
  - Filters equipment by `verification_date` within selected period
  - Client-side calculation from main table data (already filtered by department for laborants)
  - Archive data loaded on-demand for failed verification count
- **Statistics Sections**:
  1. **General**: Total equipment verified in period
  2. **By Type**: Breakdown by verification_type (verification/calibration/certification)
  3. **Failed**: Count from archive with reason "Извещение о непригодности" (department-specific)
  4. **By Status**: Fit and in storage counts from verified equipment
- **Data Flow**:
  - Receives `equipmentData` prop from MainTable (source array)
  - Loads archive data via `GET /archive/` when modal opens
  - Filters by currentUser.department for failed verification count
  - All calculations in computed property `statistics`
- **UI Integration**:
  - "Статистика" button next to "Документы" button (type="primary")
  - Modal window with NDatePicker (daterange type)
  - 4 NCard sections with stat-row styling
  - Color coding: failed (red #d03050), fit (green #18a058), others (black #333)
- **Access**: All authenticated users (laborants see department-filtered data automatically)
- **Location**: `frontend/src/components/LaborantStatistics.vue`, button in MainTable.vue line 764-766

## Important Notes

- **Language**: Project documentation and code comments are in Russian (oil & gas industry domain)
- **Communication**: Always respond in Russian ("Общайся на русском языке")
- **Verification logic**: Verification dates and status calculations are critical business logic
- **Data integrity**: Equipment deletion cascades to all related entities (verification, responsibility, finance)
- **Fixed value lists**:
  - **Departments**: 12 options stored as technical values (e.g., `lbr`, `gtl`, `smtsik`) but displayed as labels (e.g., 'ЛБР', 'ГТЛ', 'СМТСиК')
  - **Responsible persons**: 19 options with technical values (e.g., `enazarov`) displayed as labels (e.g., 'Назаров Е.')
  - Enforced via frontend `<n-select>` only, NOT in DB constraints
  - Department mapping used in: EquipmentModal.vue, MainTable.vue, UserProfile.vue
- **Laborant filtering**: Laborants see only equipment from their department (frontend filtering in MainTable.vue loadData)

## Recent Fixes

### Critical Fixes Summary

**Status Calculation (2025-10-21)**: Fixed PostgreSQL trigger bug where non-work states (storage/verification/repair) were incorrectly showing status_expired. Now state-based statuses ALWAYS override date-based statuses. Fixed 278 existing records.

**RevoGrid Data Transformation (2025-10-20)**: Implemented `transformedSource` pattern - enum fields and dates converted to Russian labels BEFORE passing to RevoGrid. Enables filtering/sorting/search with Russian labels while maintaining technical values in database.

**Finance Fields Integration (2025-10-20)**: Added `budget_item` and `code_rate` fields to equipment CRUD operations (frontend forms, backend responses, archive operations). Budget_item is required, code_rate is optional.

**Missing API Fields (2025-10-21)**: Added `registry_number` and `equipment_year` to SQL queries, Pydantic schemas, and API responses - fields existed in DB but weren't returned by backend.

### Recent Features

**Metrics Dashboard - "Списано" metric (2025-11-03)**: Added "Списано" (failed) metric to main dashboard showing count of equipment archived with reason "Извещение о непригодности". Loads archive data on mount, filters by department for laborants.

**Excel Data Export (2025-11-03)**: Added Excel export functionality to Backup panel. Admin can export entire database to .xlsx format with Russian column headers, auto-sized columns, and timestamped filenames. Uses pandas + openpyxl.

**Laborant Statistics (2025-10-25)**: Verification statistics dashboard with date range filtering. Shows total verified, breakdown by type, failed verifications (from archive), and status breakdown. Department-filtered for laborants.

**Document Generation (2025-10-25)**: Batch label generation and conservation acts using docxtpl templates. Table border preservation, automatic row numbering, full equipment data context.

**Analytics Dashboard (2025-10-25)**: Admin verification calendar by department/month. Client-side calculation, automatic year detection, visual highlighting for non-zero values.

**Contracts Notebook (2025-10-25)**: Admin-only contract balance tracking with RevoGrid editable table and PostgreSQL computed balance column.

**UI Improvements (2025-10-25)**: Clickable logo navigation, filter access for laborants (Finance/Responsibility sections hidden), terminology consistency ("На консервации" instead of "на хранении")

## Known Issues

- **Alembic config**: `alembic.ini` line 87 has hardcoded database credentials (should use `.env`)
- **Finance FK naming**: Finance model uses `equipment_model_id` (inconsistent with other FK naming - should be `equipment_id`)
- **Docs versioning**: `docs/` directory is in `.gitignore` - documentation files are local-only (not version controlled)
- **File storage**: No periodic cleanup for orphaned files (if upload fails after file save but before DB commit)

## Test Users

After running seed script (`uv run python backend/scripts/seed_users.py`):
- **Admin**: `admin` / `admin123`
- **Laborants**: `ivanov`, `petrova`, `sidorov`, `volkov`, etc. / `lab123`

## Documentation

### Руководства по развертыванию и установке

Все руководства находятся в **`docs/guides/`**:

- 📋 **README.md** - Оглавление всех руководств
- 📋 **INDEX.txt** - Навигация по руководствам

**Развертывание:**
- 🎯 **ЧТО_БРАТЬ_НА_ФЛЕШКУ.txt** - Шпаргалка для переноса на флешку
- 📖 **DEPLOYMENT_GUIDE.md** - Полное руководство по развертыванию

**Backup и восстановление:**
- 🎯 **БЫСТРАЯ_ИНСТРУКЦИЯ_BACKUP.txt** - Шпаргалка по backup
- 📖 **BACKUP_RESTORE_GUIDE.md** - Подробное руководство по backup

**Установщики:**
- 📖 **RESULTS_SUMMARY.md** - Что готово к использованию
- 📖 **BUILD_INSTRUCTIONS.md** - Как собрать установщики
- 📖 **INSTALLER_STATUS.md** - Технический статус

**Импорт данных:**
- 📖 **docs/data_import_guide.md** - Импорт из Excel

## Repository Information

- **GitHub Repository**: https://github.com/NazarovEvgn/deltica
- **Owner**: NazarovEvgn
- **Main Branch**: `main`
