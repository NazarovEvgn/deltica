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
# Windows PowerShell
.\start.ps1

# Windows CMD
start.bat
```
Эти скрипты запустят backend и frontend одновременно в отдельных окнах.

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
# Run all tests
uv run pytest

# Run specific test file
uv run pytest backend/tests/test_status_calculation.py

# Run with verbose output
uv run pytest -v

# Note: Tests currently have import issues (ModuleNotFoundError: No module named 'backend')
# This needs to be fixed by adding proper PYTHONPATH configuration or using relative imports
```

## Architecture

### Backend Structure
```
backend/
├── core/           # Application core (config, database, main)
│   ├── config.py       # Environment config via pydantic-settings
│   ├── database.py     # SQLAlchemy engine and session
│   └── main.py         # FastAPI app instance
├── app/            # Domain models and schemas
│   ├── models.py       # SQLAlchemy ORM models
│   └── schemas.py      # Pydantic schemas for API
├── services/       # Business logic layer
│   └── main_table.py   # MainTableService with CRUD logic
├── routes/         # API endpoints
│   └── main_table.py   # Main table router at /main-table
└── tests/          # Test directory (currently empty)
```

### Database Schema
**Core entities with relationships:**

1. **Equipment** - Basic equipment info (name, model, type, factory_number, inventory_number, year)
   - One-to-many relationship with Verification
   - One-to-one relationships with Responsibility and Finance (via equipment_id FK)

2. **Verification** - Verification details (type, dates, state, status, interval)
   - Foreign key to Equipment (equipment_id)

3. **Responsibility** - Ownership data (department, responsible_person, verifier_org)
   - Foreign key to Equipment (equipment_id)

4. **Finance** - Cost and payment tracking (cost_rate, quantity, coefficient, total_cost, invoice, payment)
   - Foreign key to Equipment (equipment_model_id)

### API Endpoints

Current implementation in `backend/routes/main_table.py`:
- `GET /main-table/` - Get all equipment with joined verification and responsibility data
- `GET /main-table/{equipment_id}` - Get single equipment by ID with all related data
- `GET /main-table/{equipment_id}/full` - Get complete equipment data for editing (used by frontend auto-save)
- `POST /main-table/` - Create new equipment with all related entities (verification, responsibility, finance)
- `PUT /main-table/{equipment_id}` - Update equipment and all related entities
- `DELETE /main-table/{equipment_id}` - Delete equipment and cascade delete all related entities

### Database Configuration

- **Environment variables**: Configure in `.env` file (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
- **Config**: `backend/core/config.py` uses pydantic-settings to read `.env` and build DATABASE_URL
- **Default connection**: `postgresql://postgres:postgres@localhost:5432/deltica_db`
- **Alembic config**: `alembic.ini` has hardcoded connection string (line 87) - update if needed
- **Migration directory**: `migrations/` (active)
- **Current migration**: `22b18436b99e` (with computed verification_due column)

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
- **Database**: Models defined, migrations active (`22b18436b99e`), relationships established
  - `verification_due` as computed column: `(verification_date + interval '1 month' * verification_interval - interval '1 day')::date`
- **Frontend**: RevoGrid table with full functionality (`frontend/src/components/MainTable.vue`)
  - Date formatting: dd.mm.yyyy for dates, "Месяц ГГГГ" for verification_plan
  - Fixed lists: Department (12 items) and responsible_person (19 items) via `<n-select>`
  - Auto-fill: verification_plan defaults to verification_due month but remains editable
  - Main table columns: equipment_name, equipment_model, factory_number, inventory_number, verification_type, verification_interval, verification_date, verification_due, verification_plan, status, actions
  - Auto-save on cell edit (via `@afteredit` event → GET `/full` → PUT with updated data)
  - Range editing with auto-save (via `@beforerangeedit` event)
  - Copy-paste support (Ctrl+C / Ctrl+V) in grid
  - Double-click row to open edit modal with Naive UI form
- **Authentication**: Not yet implemented (planned: role-based access with admin/laborant roles)
- **File uploads**: Not yet implemented (planned: PDF attachments for verification certificates)
- **Archiving**: Not yet implemented (planned: separate archive table for decommissioned equipment)
- **Tests**:
  - Unit tests for status calculation in `backend/tests/test_status_calculation.py` (11 tests)
  - Verification due tests in `backend/tests/test_verification_due.py`
  - **Known issue**: Tests have import errors (ModuleNotFoundError: No module named 'backend') - needs PYTHONPATH fix

## Known Issues

- **Alembic config**: `alembic.ini` line 87 has hardcoded database credentials (should use `.env`)
- **Finance FK naming**: Finance model uses `equipment_model_id` (inconsistent with other FK naming - should be `equipment_id`)
- **Test imports**: Tests fail with `ModuleNotFoundError: No module named 'backend'` - needs PYTHONPATH configuration or pytest.ini with pythonpath setting
- **Docs versioning**: `docs/` directory is in `.gitignore` - documentation files are local-only (not version controlled)

## Documentation

- `docs/deltica_architecture.md` - Architectural overview and component structure
- `docs/deltica_dev_plan.md` - Development roadmap and feature priorities
- `docs/deltica_description.md` - Domain description and business requirements
- UI mockups in PDF format in `docs/`

## Repository Information

- **GitHub Repository**: https://github.com/NazarovEvgn/deltica
- **Owner**: NazarovEvgn
- **Main Branch**: `main`
