# deltica/backend/tests/test_archive.py

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from datetime import date, datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import (
    Equipment, Verification, Responsibility, Finance, EquipmentFile,
    ArchivedEquipment, ArchivedVerification, ArchivedResponsibility,
    ArchivedFinance, ArchivedEquipmentFile
)
from backend.services.archive import ArchiveService


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
    # Создаем все необходимые таблицы для тестов архивирования
    with engine.connect() as conn:
        # Основные таблицы
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
            CREATE TABLE IF NOT EXISTS verification (
                id INTEGER PRIMARY KEY,
                equipment_id INTEGER NOT NULL,
                verification_type VARCHAR NOT NULL,
                registry_number VARCHAR,
                verification_interval INTEGER NOT NULL,
                verification_date DATE NOT NULL,
                verification_due DATE,
                verification_plan DATE NOT NULL,
                verification_state VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                FOREIGN KEY (equipment_id) REFERENCES equipment(id)
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS responsibility (
                id INTEGER PRIMARY KEY,
                equipment_id INTEGER NOT NULL,
                department VARCHAR NOT NULL,
                responsible_person VARCHAR NOT NULL,
                verifier_org VARCHAR NOT NULL,
                FOREIGN KEY (equipment_id) REFERENCES equipment(id)
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS finance (
                id INTEGER PRIMARY KEY,
                equipment_model_id INTEGER NOT NULL,
                budget_item VARCHAR NOT NULL,
                code_rate VARCHAR,
                cost_rate REAL,
                quantity INTEGER NOT NULL,
                coefficient REAL DEFAULT 1.0,
                total_cost REAL,
                invoice_number VARCHAR,
                paid_amount REAL,
                payment_date DATE,
                FOREIGN KEY (equipment_model_id) REFERENCES equipment(id)
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

        # Архивные таблицы
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS archived_equipment (
                id INTEGER PRIMARY KEY,
                original_id INTEGER NOT NULL,
                equipment_name VARCHAR NOT NULL,
                equipment_model VARCHAR NOT NULL,
                equipment_type VARCHAR NOT NULL,
                equipment_specs VARCHAR,
                factory_number VARCHAR NOT NULL,
                inventory_number VARCHAR NOT NULL,
                equipment_year INTEGER NOT NULL,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                archive_reason VARCHAR
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS archived_verification (
                id INTEGER PRIMARY KEY,
                archived_equipment_id INTEGER NOT NULL,
                original_equipment_id INTEGER NOT NULL,
                verification_type VARCHAR NOT NULL,
                registry_number VARCHAR,
                verification_interval INTEGER NOT NULL,
                verification_date DATE NOT NULL,
                verification_due DATE NOT NULL,
                verification_plan DATE NOT NULL,
                verification_state VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                FOREIGN KEY (archived_equipment_id) REFERENCES archived_equipment(id) ON DELETE CASCADE
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS archived_responsibility (
                id INTEGER PRIMARY KEY,
                archived_equipment_id INTEGER NOT NULL,
                original_equipment_id INTEGER NOT NULL,
                department VARCHAR NOT NULL,
                responsible_person VARCHAR NOT NULL,
                verifier_org VARCHAR NOT NULL,
                FOREIGN KEY (archived_equipment_id) REFERENCES archived_equipment(id) ON DELETE CASCADE
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS archived_finance (
                id INTEGER PRIMARY KEY,
                archived_equipment_id INTEGER NOT NULL,
                original_equipment_id INTEGER NOT NULL,
                budget_item VARCHAR NOT NULL,
                code_rate VARCHAR,
                cost_rate REAL,
                quantity INTEGER NOT NULL,
                coefficient REAL DEFAULT 1.0,
                total_cost REAL,
                invoice_number VARCHAR,
                paid_amount REAL,
                payment_date DATE,
                FOREIGN KEY (archived_equipment_id) REFERENCES archived_equipment(id) ON DELETE CASCADE
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS archived_equipment_files (
                id INTEGER PRIMARY KEY,
                archived_equipment_id INTEGER NOT NULL,
                original_equipment_id INTEGER NOT NULL,
                file_name VARCHAR NOT NULL,
                file_path VARCHAR NOT NULL,
                file_type VARCHAR NOT NULL DEFAULT 'other',
                file_size INTEGER NOT NULL,
                uploaded_at TIMESTAMP NOT NULL,
                FOREIGN KEY (archived_equipment_id) REFERENCES archived_equipment(id) ON DELETE CASCADE
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
            conn.execute(text("DROP TABLE IF EXISTS archived_equipment_files"))
            conn.execute(text("DROP TABLE IF EXISTS archived_finance"))
            conn.execute(text("DROP TABLE IF EXISTS archived_responsibility"))
            conn.execute(text("DROP TABLE IF EXISTS archived_verification"))
            conn.execute(text("DROP TABLE IF EXISTS archived_equipment"))
            conn.execute(text("DROP TABLE IF EXISTS equipment_files"))
            conn.execute(text("DROP TABLE IF EXISTS finance"))
            conn.execute(text("DROP TABLE IF EXISTS responsibility"))
            conn.execute(text("DROP TABLE IF EXISTS verification"))
            conn.execute(text("DROP TABLE IF EXISTS equipment"))
            conn.commit()


@pytest.fixture
def full_equipment(db_session):
    """Создать полное оборудование со всеми связанными данными."""
    # Создать оборудование
    equipment = Equipment(
        equipment_name="Манометр образцовый",
        equipment_model="МО-250",
        equipment_type="SI",
        equipment_specs="Диапазон 0-25 МПа",
        factory_number="12345",
        inventory_number="INV-001",
        equipment_year=2020
    )
    db_session.add(equipment)
    db_session.flush()

    # Создать поверку
    verification = Verification(
        equipment_id=equipment.id,
        verification_type="verification",
        registry_number="123456",
        verification_interval=12,
        verification_date=date(2024, 1, 15),
        verification_due=date(2025, 1, 14),
        verification_plan=date(2025, 1, 1),
        verification_state="state_work",
        status="status_fit"
    )
    db_session.add(verification)

    # Создать ответственность
    responsibility = Responsibility(
        equipment_id=equipment.id,
        department="Лаборатория метрологии",
        responsible_person="Иванов И.И.",
        verifier_org="ФБУ Ростест-Москва"
    )
    db_session.add(responsibility)

    # Создать финансы
    finance = Finance(
        equipment_model_id=equipment.id,
        budget_item="01.02.03.4",  # Обязательное поле
        code_rate="ТР-001",  # Опциональное поле
        cost_rate=5000.0,
        quantity=1,
        coefficient=1.2,
        total_cost=6000.0,
        invoice_number="ИНВ-2024-001",
        paid_amount=6000.0,
        payment_date=date(2024, 1, 10)
    )
    db_session.add(finance)

    # Создать файл
    eq_file = EquipmentFile(
        equipment_id=equipment.id,
        file_name="certificate.pdf",
        file_path="uploads/equipment_1/certificate.pdf",
        file_type="certificate",
        file_size=102400,
        uploaded_at=datetime(2024, 1, 16, 10, 30, 0)
    )
    db_session.add(eq_file)

    db_session.commit()
    db_session.refresh(equipment)

    return equipment


# ==================== ТЕСТЫ ====================

def test_archive_equipment_basic(db_session, full_equipment):
    """Тест базового архивирования оборудования"""
    service = ArchiveService(db_session)
    equipment_id = full_equipment.id

    # Архивируем
    archived = service.archive_equipment(equipment_id, archive_reason="Списано по акту")

    # Проверяем, что архивная запись создана
    assert archived is not None
    assert archived.original_id == equipment_id
    assert archived.equipment_name == "Манометр образцовый"
    assert archived.archive_reason == "Списано по акту"
    assert archived.archived_at is not None

    # Проверяем, что оригинальное оборудование удалено
    original_equipment = db_session.query(Equipment).filter(Equipment.id == equipment_id).first()
    assert original_equipment is None


def test_archive_equipment_with_all_relations(db_session, full_equipment):
    """Тест архивирования со всеми связанными записями"""
    service = ArchiveService(db_session)
    equipment_id = full_equipment.id

    # Архивируем
    archived = service.archive_equipment(equipment_id)

    # Проверяем архивную верификацию
    archived_verification = db_session.query(ArchivedVerification).filter(
        ArchivedVerification.archived_equipment_id == archived.id
    ).first()
    assert archived_verification is not None
    assert archived_verification.verification_type == "verification"
    assert archived_verification.registry_number == "123456"
    assert archived_verification.verification_interval == 12

    # Проверяем архивную ответственность
    archived_responsibility = db_session.query(ArchivedResponsibility).filter(
        ArchivedResponsibility.archived_equipment_id == archived.id
    ).first()
    assert archived_responsibility is not None
    assert archived_responsibility.department == "Лаборатория метрологии"
    assert archived_responsibility.responsible_person == "Иванов И.И."

    # Проверяем архивные финансы
    archived_finance = db_session.query(ArchivedFinance).filter(
        ArchivedFinance.archived_equipment_id == archived.id
    ).first()
    assert archived_finance is not None
    assert archived_finance.cost_rate == 5000.0
    assert archived_finance.invoice_number == "ИНВ-2024-001"

    # Проверяем архивные файлы
    archived_file = db_session.query(ArchivedEquipmentFile).filter(
        ArchivedEquipmentFile.archived_equipment_id == archived.id
    ).first()
    assert archived_file is not None
    assert archived_file.file_name == "certificate.pdf"
    assert archived_file.file_size == 102400


def test_archive_equipment_deletes_originals(db_session, full_equipment):
    """Тест удаления оригинальных записей при архивировании"""
    service = ArchiveService(db_session)
    equipment_id = full_equipment.id

    # Получаем ID связанных записей
    verification_id = db_session.query(Verification).filter(
        Verification.equipment_id == equipment_id
    ).first().id

    # Архивируем
    service.archive_equipment(equipment_id)

    # Проверяем, что все оригинальные записи удалены
    assert db_session.query(Equipment).filter(Equipment.id == equipment_id).first() is None
    assert db_session.query(Verification).filter(Verification.id == verification_id).first() is None
    assert db_session.query(Responsibility).filter(Responsibility.equipment_id == equipment_id).first() is None
    assert db_session.query(Finance).filter(Finance.equipment_model_id == equipment_id).first() is None
    assert db_session.query(EquipmentFile).filter(EquipmentFile.equipment_id == equipment_id).first() is None


def test_archive_nonexistent_equipment(db_session):
    """Тест архивирования несуществующего оборудования"""
    service = ArchiveService(db_session)

    # Пытаемся заархивировать несуществующее оборудование
    archived = service.archive_equipment(99999)

    assert archived is None


def test_get_all_archived(db_session, full_equipment):
    """Тест получения всех архивных записей"""
    service = ArchiveService(db_session)

    # Архивируем оборудование
    service.archive_equipment(full_equipment.id, archive_reason="Причина 1")

    # Создаем и архивируем еще одно оборудование
    equipment2 = Equipment(
        equipment_name="Термометр",
        equipment_model="ТМ-100",
        equipment_type="SI",
        factory_number="54321",
        inventory_number="INV-002",
        equipment_year=2021
    )
    db_session.add(equipment2)
    db_session.commit()
    service.archive_equipment(equipment2.id, archive_reason="Причина 2")

    # Получаем все архивные записи
    archived_list = service.get_all_archived()

    assert len(archived_list) == 2
    assert archived_list[0].equipment_name in ["Манометр образцовый", "Термометр"]
    assert archived_list[1].equipment_name in ["Манометр образцовый", "Термометр"]


def test_restore_equipment_basic(db_session, full_equipment):
    """Тест базового восстановления оборудования из архива"""
    service = ArchiveService(db_session)
    original_id = full_equipment.id

    # Архивируем
    archived = service.archive_equipment(original_id)
    archived_id = archived.id

    # Восстанавливаем
    restored = service.restore_equipment(archived_id)

    # Проверяем восстановленное оборудование
    assert restored is not None
    assert restored.equipment_name == "Манометр образцовый"
    assert restored.equipment_model == "МО-250"
    assert restored.equipment_type == "SI"
    assert restored.factory_number == "12345"

    # Проверяем, что архивная запись удалена
    archived_check = db_session.query(ArchivedEquipment).filter(
        ArchivedEquipment.id == archived_id
    ).first()
    assert archived_check is None


def test_restore_equipment_with_all_relations(db_session, full_equipment):
    """Тест восстановления со всеми связанными данными"""
    service = ArchiveService(db_session)

    # Архивируем
    archived = service.archive_equipment(full_equipment.id)

    # Восстанавливаем
    restored = service.restore_equipment(archived.id)

    # Проверяем восстановленную верификацию
    verification = db_session.query(Verification).filter(
        Verification.equipment_id == restored.id
    ).first()
    assert verification is not None
    assert verification.verification_type == "verification"
    assert verification.registry_number == "123456"

    # Проверяем восстановленную ответственность
    responsibility = db_session.query(Responsibility).filter(
        Responsibility.equipment_id == restored.id
    ).first()
    assert responsibility is not None
    assert responsibility.department == "Лаборатория метрологии"

    # Проверяем восстановленные финансы
    finance = db_session.query(Finance).filter(
        Finance.equipment_model_id == restored.id
    ).first()
    assert finance is not None
    assert finance.cost_rate == 5000.0

    # Проверяем восстановленные файлы
    eq_file = db_session.query(EquipmentFile).filter(
        EquipmentFile.equipment_id == restored.id
    ).first()
    assert eq_file is not None
    assert eq_file.file_name == "certificate.pdf"


def test_restore_equipment_deletes_archived(db_session, full_equipment):
    """Тест удаления архивных записей при восстановлении"""
    service = ArchiveService(db_session)

    # Архивируем
    archived = service.archive_equipment(full_equipment.id)
    archived_id = archived.id

    # Восстанавливаем
    service.restore_equipment(archived_id)

    # Проверяем, что все архивные записи удалены
    assert db_session.query(ArchivedEquipment).filter(ArchivedEquipment.id == archived_id).first() is None
    assert db_session.query(ArchivedVerification).filter(
        ArchivedVerification.archived_equipment_id == archived_id
    ).first() is None
    assert db_session.query(ArchivedResponsibility).filter(
        ArchivedResponsibility.archived_equipment_id == archived_id
    ).first() is None
    assert db_session.query(ArchivedFinance).filter(
        ArchivedFinance.archived_equipment_id == archived_id
    ).first() is None


def test_restore_nonexistent_archived(db_session):
    """Тест восстановления несуществующей архивной записи"""
    service = ArchiveService(db_session)

    # Пытаемся восстановить несуществующую запись
    restored = service.restore_equipment(99999)

    assert restored is None


def test_delete_archived_permanently(db_session, full_equipment):
    """Тест окончательного удаления из архива"""
    service = ArchiveService(db_session)

    # Архивируем
    archived = service.archive_equipment(full_equipment.id)
    archived_id = archived.id

    # Удаляем навсегда
    result = service.delete_archived(archived_id)

    assert result is True

    # Проверяем, что запись удалена
    assert db_session.query(ArchivedEquipment).filter(
        ArchivedEquipment.id == archived_id
    ).first() is None


def test_delete_nonexistent_archived(db_session):
    """Тест удаления несуществующей архивной записи"""
    service = ArchiveService(db_session)

    # Пытаемся удалить несуществующую запись
    result = service.delete_archived(99999)

    assert result is False


def test_archive_restore_cycle_preserves_data(db_session, full_equipment):
    """Тест целостности данных при полном цикле архивирование-восстановление"""
    service = ArchiveService(db_session)

    # Сохраняем оригинальные данные
    original_name = full_equipment.equipment_name
    original_model = full_equipment.equipment_model
    original_factory = full_equipment.factory_number

    # Цикл: архивирование -> восстановление
    archived = service.archive_equipment(full_equipment.id, archive_reason="Тестовое архивирование")
    restored = service.restore_equipment(archived.id)

    # Проверяем, что данные сохранились
    assert restored.equipment_name == original_name
    assert restored.equipment_model == original_model
    assert restored.factory_number == original_factory

    # Проверяем связанные данные
    verification = db_session.query(Verification).filter(
        Verification.equipment_id == restored.id
    ).first()
    assert verification.registry_number == "123456"

    responsibility = db_session.query(Responsibility).filter(
        Responsibility.equipment_id == restored.id
    ).first()
    assert responsibility.responsible_person == "Иванов И.И."


def test_archive_equipment_without_optional_relations(db_session):
    """Тест архивирования оборудования без опциональных связей"""
    # Создаем оборудование только с обязательными полями
    equipment = Equipment(
        equipment_name="Простой прибор",
        equipment_model="ПП-1",
        equipment_type="IO",
        factory_number="99999",
        inventory_number="INV-999",
        equipment_year=2023
    )
    db_session.add(equipment)
    db_session.commit()

    service = ArchiveService(db_session)

    # Архивируем без связанных данных
    archived = service.archive_equipment(equipment.id)

    # Проверяем, что архивирование прошло успешно
    assert archived is not None
    assert archived.equipment_name == "Простой прибор"

    # Проверяем, что нет связанных архивных записей
    assert db_session.query(ArchivedVerification).filter(
        ArchivedVerification.archived_equipment_id == archived.id
    ).first() is None
    assert db_session.query(ArchivedResponsibility).filter(
        ArchivedResponsibility.archived_equipment_id == archived.id
    ).first() is None


def test_get_archived_by_id(db_session, full_equipment):
    """Тест получения архивной записи по ID"""
    service = ArchiveService(db_session)

    # Архивируем
    archived = service.archive_equipment(full_equipment.id, archive_reason="Тест получения")
    archived_id = archived.id

    # Получаем по ID
    retrieved = service.get_archived_by_id(archived_id)

    assert retrieved is not None
    assert retrieved.id == archived_id
    assert retrieved.equipment_name == "Манометр образцовый"
    assert retrieved.archive_reason == "Тест получения"


def test_get_nonexistent_archived_by_id(db_session):
    """Тест получения несуществующей архивной записи"""
    service = ArchiveService(db_session)

    retrieved = service.get_archived_by_id(99999)

    assert retrieved is None


def test_archive_reason_optional(db_session, full_equipment):
    """Тест архивирования без указания причины"""
    service = ArchiveService(db_session)

    # Архивируем без причины
    archived = service.archive_equipment(full_equipment.id)

    assert archived is not None
    assert archived.archive_reason is None
