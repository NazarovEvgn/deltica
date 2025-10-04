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
- **Backend**: FastAPI with Python 3.13 managed by uv
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Target Platform**: Tauri desktop application

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
- `POST /main-table/` - Create new equipment with all related entities (verification, responsibility, finance)
- `PUT /main-table/{equipment_id}` - Update equipment and all related entities
- `DELETE /main-table/{equipment_id}` - Delete equipment and cascade delete all related entities

### Database Configuration

- **Environment variables**: Configure in `.env` file (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
- **Config**: `backend/core/config.py` uses pydantic-settings to read `.env` and build DATABASE_URL
- **Default connection**: `postgresql://postgres:postgres@localhost:5432/deltica_db`
- **Alembic config**: `alembic.ini` has hardcoded connection string (line 87) - update if needed
- **Migration directory**: `migrations/` (active)
- **Current migration**: `f6eeca7cc210` (baseline migration)

### Key Development Patterns

- **Database sessions**: Use dependency injection via `get_db()` in routes
- **Service layer**: Business logic in services (e.g., `MainTableService`), routes handle HTTP concerns
- **Full entity CRUD**: Service methods handle creating/updating/deleting across all related tables
- **Outer joins**: Main table queries use LEFT OUTER JOIN to include equipment without verification/responsibility

## Important Notes

- **Language**: Project documentation and code comments are in Russian (oil & gas industry domain)
- **Communication**: Always respond in Russian ("Общайся на русском языке")
- **Verification logic**: Verification dates and status calculations are critical business logic
- **Data integrity**: Equipment deletion cascades to all related entities (verification, responsibility, finance)
- **Planned features**: Role-based access control, integration with ФГИС Аршин (Russian federal metrology system)

## Current Implementation Status

- **Backend**: Full CRUD API implemented at `/main-table` endpoint
- **Database**: Models defined, baseline migrations configured, relationships established
- **Frontend**: Minimal Vue.js 3 setup (placeholder content, MainTable.vue component needed)
- **Authentication**: Not yet implemented
- **Tests**: Directory exists but no tests implemented

## Known Issues

- `alembic.ini` line 87 has hardcoded database credentials (should use `.env`)
- Finance model uses `equipment_model_id` (inconsistent with other FK naming)
- Missing `__init__.py` files in some Python packages

## Documentation

- `docs/deltica_architecture.md` - Architectural overview and component structure
- `docs/deltica_dev_plan.md` - Development roadmap and feature priorities
- `docs/deltica_description.md` - Domain description and business requirements
- UI mockups in PDF format in `docs/`

## Repository Information

- **GitHub Repository**: https://github.com/NazarovEvgn/deltica
- **Owner**: NazarovEvgn
- **Main Branch**: `main`
