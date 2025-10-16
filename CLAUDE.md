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
- **Backend**: FastAPI with Python 3.13 managed by uv
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Target Platform**: Tauri desktop application (planned)

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

### Quick Start (одной командой)
```bash
# Windows PowerShell (рекомендуется)
.\start.ps1

# Windows CMD
start.bat
# или
deltica-start.bat
```
Эти скрипты запустят backend и frontend одновременно в отдельных окнах.

**Для удобной работы** можно настроить PowerShell алиас (см. README_START.md):
```powershell
# Добавить в $PROFILE:
function Start-Deltica {
    Set-Location C:\Projects\deltica
    .\start.ps1
}
Set-Alias deltica Start-Deltica
```
После этого из любой директории можно запускать просто `deltica`.

### Backend Development
```bash
# Run FastAPI backend with auto-reload (default port 8000)
uv run uvicorn backend.core.main:app --reload

# Start on different port if needed
uv run uvicorn backend.core.main:app --reload --port 8001
```

### Frontend Development
```bash
cd frontend
npm run dev        # Start development server (http://localhost:5173)
npm run build      # Build for production
npm run preview    # Preview production build
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
# Run all tests (125 total)
uv run pytest

# Run specific test categories
uv run pytest backend/tests/test_file_utils.py      # File utilities unit tests (39)
uv run pytest backend/tests/test_files_api.py       # File API integration tests (17)
uv run pytest backend/tests/test_files_security.py  # File security tests (20)
uv run pytest backend/tests/test_files_encoding.py  # File encoding tests (16)
uv run pytest backend/tests/test_status_calculation.py  # Status calculation tests (11)
uv run pytest backend/tests/test_verification_due.py    # Verification due tests (6)
uv run pytest backend/tests/test_archive.py         # Archive functionality tests (16)

# Run all file-related tests together (98 tests)
uv run pytest backend/tests/test_file*.py -v

# Run single test by name
uv run pytest backend/tests/test_files_api.py::test_upload_file_success -v

# Run with coverage report
uv run pytest backend/tests/test_file*.py --cov=backend.routes.files --cov-report=html
uv run pytest backend/tests/test_archive.py --cov=backend.services.archive --cov-report=html

# Results: All tests passing (100% success rate)
# - File tests: 98/98 passed (~1.5 seconds)
# - Status tests: 11/11 passed
# - Verification tests: 6/6 passed
# - Archive tests: 16/16 passed (~0.2 seconds)
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
│   ├── models.py       # SQLAlchemy ORM models (Equipment, Verification, EquipmentFile, etc.)
│   └── schemas.py      # Pydantic schemas for API requests/responses
├── services/       # Business logic layer
│   ├── main_table.py   # MainTableService with CRUD logic
│   └── archive.py      # ArchiveService with archive/restore/delete logic
├── routes/         # API endpoints
│   ├── main_table.py   # Main table router at /main-table
│   ├── files.py        # File management router at /files
│   └── archive.py      # Archive router at /archive
└── tests/          # Test directory with comprehensive test suite
    ├── conftest.py          # Pytest fixtures (db_session, client, temp files)
    ├── test_file_utils.py   # 39 unit tests for file utilities
    ├── test_files_api.py    # 17 integration tests for API endpoints
    ├── test_files_security.py   # 20 security tests (path traversal, limits)
    ├── test_files_encoding.py   # 16 encoding tests (Cyrillic, UTF-8)
    ├── test_status_calculation.py  # 11 tests for verification status logic
    ├── test_verification_due.py    # Tests for verification_due calculations
    ├── test_archive.py      # 16 tests for archive functionality
    └── README.md            # Test documentation and usage guide
```

### Database Schema
**Core entities with relationships:**

1. **Equipment** - Basic equipment info (name, model, type, factory_number, inventory_number, year)
   - One-to-many relationship with Verification
   - One-to-many relationship with EquipmentFile (cascade delete)
   - One-to-one relationships with Responsibility and Finance (via equipment_id FK)

2. **Verification** - Verification details (type, dates, state, status, interval)
   - Foreign key to Equipment (equipment_id)

3. **Responsibility** - Ownership data (department, responsible_person, verifier_org)
   - Foreign key to Equipment (equipment_id)

4. **Finance** - Cost and payment tracking (cost_rate, quantity, coefficient, total_cost, invoice, payment)
   - Foreign key to Equipment (equipment_model_id)

5. **EquipmentFile** - File attachments (certificates, passports, technical docs)
   - Foreign key to Equipment (equipment_id) with CASCADE DELETE
   - Fields: file_name, file_path, file_type, file_size, uploaded_at
   - File types: 'certificate', 'passport', 'technical_doc', 'other'
   - Storage: filesystem (backend/uploads/equipment_{id}/)

**Archive entities** (mirror structure of main tables):

6. **ArchivedEquipment** - Archived equipment records
   - Stores original_id, archived_at, archive_reason (optional)
   - One-to-many with ArchivedVerification, ArchivedResponsibility, ArchivedFinance, ArchivedEquipmentFile

7. **ArchivedVerification**, **ArchivedResponsibility**, **ArchivedFinance**, **ArchivedEquipmentFile** - Archived related data
   - Mirror structure of main tables with archived_equipment_id FK
   - CASCADE DELETE on archived_equipment removal

### API Endpoints

**Main Table** (`backend/routes/main_table.py`):
- `GET /main-table/` - Get all equipment with joined verification and responsibility data
- `GET /main-table/{equipment_id}` - Get single equipment by ID with all related data
- `GET /main-table/{equipment_id}/full` - Get complete equipment data for editing (used by frontend auto-save)
- `POST /main-table/` - Create new equipment with all related entities (verification, responsibility, finance)
- `PUT /main-table/{equipment_id}` - Update equipment and all related entities
- `DELETE /main-table/{equipment_id}` - Delete equipment and cascade delete all related entities

**File Management** (`backend/routes/files.py`):
- `POST /files/upload/{equipment_id}` - Upload file (PDF, DOC, DOCX, XLS, XLSX, JPG, PNG) with type selection
- `GET /files/view/{file_id}` - View file in browser (inline Content-Disposition, proper MIME type)
- `GET /files/download/{file_id}` - Download file (attachment Content-Disposition, forced download)
- `GET /files/equipment/{equipment_id}` - List all files for equipment with metadata
- `DELETE /files/{file_id}` - Delete file from database and filesystem
- **Security**: File type validation, 50 MB size limit, filename sanitization, path traversal protection
- **Encoding**: Full Cyrillic support, RFC 5987 Content-Disposition headers, UTF-8 encoding

**Archive** (`backend/routes/archive.py`):
- `POST /archive/equipment/{equipment_id}` - Archive equipment with optional archive_reason
- `GET /archive/` - List all archived equipment
- `GET /archive/{archived_equipment_id}` - Get archived equipment by ID
- `POST /archive/restore/{archived_equipment_id}` - Restore equipment from archive to main tables
- `DELETE /archive/{archived_equipment_id}` - Permanently delete from archive
- **Logic**: Copies all related data to archive tables, explicitly deletes originals (no FK CASCADE)

### Database Configuration

- **Environment variables**: Configure in `.env` file (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
- **Config**: `backend/core/config.py` uses pydantic-settings to read `.env` and build DATABASE_URL
- **Default connection**: `postgresql://postgres:postgres@localhost:5432/deltica_db`
- **Alembic config**: `alembic.ini` has hardcoded connection string (line 87) - update if needed
- **Migration directory**: `migrations/` (active)
- **Current migration**: `168ffc404f69` (head - with archive tables)

### Key Development Patterns

- **Database sessions**: Use dependency injection via `get_db()` in routes
- **Service layer**: Business logic in services (e.g., `MainTableService`), routes handle HTTP concerns
- **Full entity CRUD**: Service methods handle creating/updating/deleting across all related tables
- **Outer joins**: Main table queries use LEFT OUTER JOIN to include equipment without verification/responsibility
- **Status calculation**: Application-level logic in `backend/services/main_table.py::calculate_status()`. Status depends on both `verification_due` (from DB computed column) and `verification_state`. Non-work states (storage/verification/repair/archived) always override date-based statuses.
- **Fixed value lists**: Department (12 options) and responsible_person (19 options) are enforced via frontend `<n-select>` only, not in DB constraints
- **Date formatting**: Use `formatDate()` for dd.mm.yyyy display, `formatMonthYear()` for "Месяц ГГГГ" display in tables
- **RevoGrid features**:
  - **cellTemplates**: For custom rendering (date formatting, status mapping, action buttons). Example:
    ```javascript
    {
      prop: 'verification_date',
      cellTemplate: (createElement, props) => {
        return createElement('span', {
          textContent: formatDate(props.model[props.prop]),
          style: { padding: '0 4px' }
        })
      }
    }
    ```
  - **Auto-save**: Cell edits trigger `@afteredit` event, which calls `/full` endpoint to get complete data, updates changed field, then PUT to save
  - **Range editing**: Supports drag-to-fill and copy-paste (Ctrl+C/Ctrl+V), handled via `@beforerangeedit` event
  - **Double-click**: Opens edit modal for full equipment editing
  - **Read-only columns**: Set `readonly: true` for computed fields (verification_due, status, actions)

## Important Notes

- **Language**: Project documentation and code comments are in Russian (oil & gas industry domain)
- **Communication**: Always respond in Russian ("Общайся на русском языке")
- **Verification logic**: Verification dates and status calculations are critical business logic
- **Data integrity**: Equipment deletion cascades to all related entities (verification, responsibility, finance)
- **Planned features**: Role-based access control, integration with ФГИС Аршин (Russian federal metrology system)

## Current Implementation Status

- **Backend**: Full CRUD API implemented at `/main-table` endpoint
  - Application-level status calculation based on `verification_due` and `verification_state`
  - Flush/refresh pattern to retrieve DB-computed `verification_due` before status calculation
- **Database**: Models defined, migrations active (current: `168ffc404f69`), relationships established
  - Migration `22b18436b99e`: Added `verification_due` as computed column: `(verification_date + interval '1 month' * verification_interval - interval '1 day')::date`
  - Migration `88f8d0e8cb6d`: Added `equipment_files` table with CASCADE DELETE on equipment removal
  - Migration `168ffc404f69`: Added archive tables (archived_equipment, archived_verification, archived_responsibility, archived_finance, archived_equipment_files)
- **Frontend**: RevoGrid table with full functionality (`frontend/src/components/MainTable.vue`)
  - Date formatting: dd.mm.yyyy for dates, "Месяц ГГГГ" for verification_plan
  - Fixed lists: Department (12 items) and responsible_person (19 items) via `<n-select>`
  - Auto-fill: verification_plan defaults to verification_due month but remains editable
  - Main table columns: equipment_name, equipment_model, factory_number, inventory_number, verification_type, verification_interval, verification_date, verification_due, verification_plan, status, actions
  - Auto-save on cell edit (via `@afteredit` event → GET `/full` → PUT with updated data)
  - Range editing with auto-save (via `@beforerangeedit` event)
  - Copy-paste support (Ctrl+C / Ctrl+V) in grid
  - Double-click row to open edit modal with Naive UI form
- **File Management** (`frontend/src/components/EquipmentModal.vue`):
  - ✅ Drag-n-drop file upload (Naive UI NUploadDragger)
  - ✅ File type selection (certificate/passport/technical_doc/other)
  - ✅ File list with metadata (name, type, size, upload date)
  - ✅ Click filename to view in browser (new tab)
  - ✅ Download button for file sharing
  - ✅ Delete button with confirmation
  - ✅ Full Cyrillic filename support
  - Icons from @vicons/ionicons5
- **Archiving** (`frontend/src/components/ArchiveTable.vue`, `backend/routes/archive.py`):
  - ✅ "В архив" button in equipment edit modal with confirmation dialog
  - ✅ Separate archive view accessible via "Архив" button in main table
  - ✅ Archive service with full cycle: archive, restore, delete permanently
  - ✅ 5 archive tables mirror main structure (archived_equipment, archived_verification, etc.)
  - ✅ Explicit deletion of related records (no CASCADE on FK level)
  - ✅ Archive table displays: name, model, factory/inventory numbers, type, archived_at, archive_reason
  - ✅ Restore functionality returns equipment to main table
  - ✅ Permanent delete with warning confirmation
- **Authentication**: Not yet implemented (planned: role-based access with admin/laborant roles)
- **Tests**: Comprehensive test suite (125 tests total)
  - ✅ Status calculation tests: `test_status_calculation.py` (11 tests) - validates status calculation based on verification_due and verification_state
  - ✅ Verification due tests: `test_verification_due.py` (6+ tests) - validates computed column for verification_due dates
  - ✅ File utilities tests: `test_file_utils.py` (39 unit tests) - file extensions, MIME types, sanitization, validation
  - ✅ File API tests: `test_files_api.py` (17 integration tests) - upload, view, download, delete, cascade delete
  - ✅ Security tests: `test_files_security.py` (20 tests) - path traversal, size limits, injections, parallel uploads
  - ✅ Encoding tests: `test_files_encoding.py` (16 tests) - Cyrillic filenames, UTF-8, RFC 5987 headers
  - ✅ Archive tests: `test_archive.py` (16 tests) - archive, restore, delete, data integrity, full cycle
  - All tests passing (100% success rate)
  - Test documentation: `backend/tests/README.md` with detailed coverage breakdown

## Known Issues

- **Alembic config**: `alembic.ini` line 87 has hardcoded database credentials (should use `.env`)
- **Finance FK naming**: Finance model uses `equipment_model_id` (inconsistent with other FK naming - should be `equipment_id`)
- **Docs versioning**: `docs/` directory is in `.gitignore` - documentation files are local-only (not version controlled)
- **File storage**: No periodic cleanup for orphaned files (if upload fails after file save but before DB commit)
- **Disk space**: No validation of available disk space before file upload

## Documentation

- `docs/deltica_architecture.md` - Architectural overview and component structure
- `docs/deltica_dev_plan.md` - Development roadmap and feature priorities
- `docs/deltica_description.md` - Domain description and business requirements
- `backend/tests/README.md` - Comprehensive test documentation (98 file tests, 11 status tests)
- `README_START.md` - Quick start guide with PowerShell alias setup
- UI mockups in PDF format in `docs/`

**Note**: `docs/` directory is in `.gitignore` - documentation files are local-only (not version controlled)

## Repository Information

- **GitHub Repository**: https://github.com/NazarovEvgn/deltica
- **Owner**: NazarovEvgn
- **Main Branch**: `main`
