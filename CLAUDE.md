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
- `/main-table/*` - CRUD operations for equipment with joined verification/responsibility data
- `/files/*` - File upload/download/view with Cyrillic support (RFC 5987 headers)
- `/archive/*` - Archive/restore/delete with explicit deletion (no FK CASCADE)
- `/auth/*` - JWT authentication (24-hour expiration), bcrypt password hashing
- `/pinned-documents/*` - Shared PDF documents (view/download for all, upload/delete admin-only)

### Critical Development Patterns

**1. Status Calculation Logic** (`backend/services/main_table.py::calculate_status()`):
- Status depends on BOTH `verification_due` (computed column) and `verification_state`
- Non-work states (storage/verification/repair/archived) ALWAYS override date-based statuses
- Must call `db.flush()` and `db.refresh(equipment)` before calculating status to get computed `verification_due`

**2. Archive Operations** (`backend/services/archive.py`):
- Archive process: Copy to archive tables → Explicitly delete from main tables
- NO FK CASCADE on archive level - deletion is explicit in service layer
- Restore process: Copy back to main tables → Delete from archive tables

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
- Main table queries use LEFT OUTER JOIN to include equipment without verification/responsibility

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

## Important Notes

- **Language**: Project documentation and code comments are in Russian (oil & gas industry domain)
- **Communication**: Always respond in Russian ("Общайся на русском языке")
- **Verification logic**: Verification dates and status calculations are critical business logic
- **Data integrity**: Equipment deletion cascades to all related entities (verification, responsibility, finance)
- **Fixed value lists**: Department (12 options) and responsible_person (19 options) enforced via frontend `<n-select>` only, NOT in DB constraints

## Known Issues

- **Alembic config**: `alembic.ini` line 87 has hardcoded database credentials (should use `.env`)
- **Finance FK naming**: Finance model uses `equipment_model_id` (inconsistent with other FK naming - should be `equipment_id`)
- **Docs versioning**: `docs/` directory is in `.gitignore` - documentation files are local-only (not version controlled)
- **File storage**: No periodic cleanup for orphaned files (if upload fails after file save but before DB commit)

## Test Users

After running seed script (`uv run python backend/scripts/seed_users.py`):
- **Admin**: `admin` / `admin123`
- **Laborants**: `ivanov`, `petrova`, `sidorov`, `volkov`, etc. / `lab123`

## Repository Information

- **GitHub Repository**: https://github.com/NazarovEvgn/deltica
- **Owner**: NazarovEvgn
- **Main Branch**: `main`
