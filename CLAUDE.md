# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Deltica is a metrology equipment management system for oil & gas companies. It tracks metrology equipment (measuring instruments and testing equipment) and their verification schedules (calibration, verification, certification).

**Key Domain Concepts:**
- **Equipment Types**: СИ (measuring instruments), ИО (testing equipment)
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
# Edit .env with your database credentials

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend && npm install
```

### Frontend Development
```bash
cd frontend
npm run dev        # Start development server (http://localhost:5173)
npm run build      # Build for production
npm run preview    # Preview production build
```

### Backend Development
```bash
# Run FastAPI backend with auto-reload
uv run uvicorn backend.core.main:app --reload

# Start on different port if needed
uv run uvicorn backend.core.main:app --reload --port 8001
```

### Database Management
```bash
# Check current migration status
uv run alembic current

# View migration history
uv run alembic history

# Create new migrations (when schema changes)
uv run alembic revision --autogenerate -m "Description"

# Apply migrations to database
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Database Setup
- **Environment Configuration**: Copy `.env.example` to `.env` and configure database credentials
- **Connection**: Default `postgresql://postgres:postgres@localhost:5432/deltica_db`
- **Configuration**: `backend/core/config.py` reads from `.env` using pydantic-settings
- **Models**: Defined in `backend/app/models.py`
- **Migration Directory**: `migrations/` (active), `alembic/` (legacy)
- **Current Migration**: `f6eeca7cc210` (baseline migration - assumes existing tables)

## Architecture

### Backend Structure
```
backend/
├── core/           # Application core (config, database, main)
├── app/            # Domain models and schemas
├── services/       # Business logic layer (equipment service implemented)
├── routes/         # API endpoints (equipment router implemented)
└── tests/          # Test directory (currently empty)
```

### Database Schema
**Core entities with relationships:**

1. **Equipment** (метрологическое оборудование)
   - Basic equipment info (name, model, type, factory number, etc.)
   - One-to-many with Verification

2. **Verification** (верификация)
   - Verification details (type, dates, status, state)
   - Foreign key to Equipment

3. **Responsibility** (ответственность)
   - Ownership data (department, responsible person, verifier org)
   - Foreign key to Equipment

4. **Finance** (финансы)
   - Cost and payment tracking
   - Foreign key to Equipment

### Key Enums
- **Equipment Type**: 'SI', 'IO'
- **Verification Type**: 'calibration', 'verification', 'certification'
- **Verification State**: 'state_work', 'state_storage', 'state_verification', 'state_repair', 'state_archived'
- **Status**: 'status_fit', 'status_expired', 'status_expiring', 'status_storage', 'status_verification', 'status_repair'

## Development Patterns

- **Models**: SQLAlchemy models in `backend/app/models.py`
- **Schemas**: Pydantic schemas for API serialization in `backend/app/schemas.py`
- **Services**: Business logic organized by domain (equipment, verification, auth)
- **Routes**: FastAPI routers organized by domain
- **Database**: Dependency injection pattern for database sessions

## Important Notes

- Project documentation is in Russian (business domain from Russian oil & gas industry)
- Role-based access control: Admin can perform CRUD operations, Laborant has read-only access to their department's equipment
- Verification dates and status calculations are critical business logic
- Frontend will have different interfaces based on user role
- Integration planned with ФГИС Аршин (Russian federal metrology information system)

## Current Implementation Status

- **API Endpoints**: Equipment CRUD operations implemented at `/equipment`
- **Authentication**: Not yet implemented
- **Database**: Models defined, baseline migrations configured
- **Frontend**: Minimal Vue.js 3 setup (placeholder content)
- **Tests**: Directory exists but no tests implemented

## Known Issues

- Database configuration inconsistency between `database.py` and `config.py`
- Migration files are empty baseline migrations
- Hardcoded database credentials in some files
- Missing `__init__.py` files in some Python packages

## Documentation

- Project documentation available in `docs/` directory
- Architecture details in `docs/deltica_architecture.md`
- Domain description in `docs/deltica_description.md`
- UI mockups in PDF format in `docs/`

## Development Focus Areas

1. **Current**: Fix database configuration, implement remaining API endpoints
2. **Next**: Authentication system, frontend data display
3. **Phase 2**: Advanced filtering and admin interfaces
4. **Phase 3**: Document management and file uploads
- Общайся на русском языке