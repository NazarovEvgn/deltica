# deltica/backend/tests/conftest.py

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import tempfile
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.core.main import app
from backend.core.database import Base, get_db
from backend.app.models import Equipment, Verification, Responsibility, Finance, EquipmentFile


# Используем in-memory SQLite для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Создать тестовую БД сессию для каждого теста."""
    # Для SQLite создаем только нужные таблицы, пропуская computed columns
    # которые используют PostgreSQL-specific синтаксис

    # Создаем таблицы вручную для тестовой SQLite БД
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY,
                equipment_name VARCHAR NOT NULL,
                equipment_model VARCHAR NOT NULL,
                equipment_type VARCHAR NOT NULL,
                equipment_specs VARCHAR,
                factory_number VARCHAR NOT NULL,
                inventory_number VARCHAR NOT NULL,
                equipment_year INTEGER NOT NULL
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS equipment_files (
                id INTEGER PRIMARY KEY,
                equipment_id INTEGER NOT NULL,
                file_name VARCHAR NOT NULL,
                file_path VARCHAR NOT NULL,
                file_type VARCHAR NOT NULL DEFAULT 'other',
                file_size INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
            )
        """))
        conn.commit()

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Очищаем таблицы
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS equipment_files"))
            conn.execute(text("DROP TABLE IF EXISTS equipment"))
            conn.commit()


@pytest.fixture(scope="function")
def client(db_session):
    """Создать FastAPI TestClient с тестовой БД."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_upload_dir(monkeypatch):
    """Создать временную директорию для загрузки файлов."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Переопределяем UPLOAD_DIR в модуле files
    from backend.routes import files
    monkeypatch.setattr(files, "UPLOAD_DIR", temp_path)

    yield temp_path

    # Очистка после теста
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_equipment(db_session):
    """Создать тестовое оборудование в БД."""
    equipment = Equipment(
        equipment_name="Тестовый манометр",
        equipment_model="МТ-100",
        equipment_type="SI",
        factory_number="12345",
        inventory_number="INV-001",
        equipment_year=2020
    )
    db_session.add(equipment)
    db_session.commit()
    db_session.refresh(equipment)
    return equipment


@pytest.fixture
def sample_pdf_file():
    """Создать тестовый PDF файл."""
    content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    return ("test_document.pdf", content, "application/pdf")


@pytest.fixture
def sample_image_file():
    """Создать тестовый PNG файл (минимальный валидный PNG)."""
    # Минимальный валидный PNG (1x1 прозрачный пиксель)
    content = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return ("test_image.png", content, "image/png")


@pytest.fixture
def sample_cyrillic_file():
    """Создать тестовый файл с кириллическим именем."""
    content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    return ("Сертификат поверки №123.pdf", content, "application/pdf")


@pytest.fixture
def large_file():
    """Создать файл размером больше лимита (51 МБ)."""
    # 51 * 1024 * 1024 байт
    content = b"x" * (51 * 1024 * 1024)
    return ("large_file.pdf", content, "application/pdf")


@pytest.fixture
def invalid_extension_file():
    """Создать файл с недопустимым расширением."""
    content = b"#!/bin/bash\necho 'malicious script'"
    return ("malicious.sh", content, "application/x-sh")
