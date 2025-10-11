# backend/tests/test_verification_due.py

"""
Unit тест для проверки корректности вычисления verification_due.

Формула: verification_due = verification_date + verification_interval (месяцев) - 1 день

Тест: verification_date = 08.10.2025, verification_interval = 24
Ожидаемый результат: verification_due = 07.10.2027 (08.10.2025 + 24 месяца - 1 день)
"""

import pytest
from datetime import date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings
from backend.core.database import Base
from backend.app.models import Equipment, Verification


@pytest.fixture(scope="module")
def test_db():
    """Создание тестовой сессии БД."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()


def test_verification_due_calculation(test_db):
    """
    Тест корректности вычисления verification_due.

    Дано: verification_date = 08.10.2025, verification_interval = 24 месяца
    Ожидается: verification_due = 07.10.2027
    """
    # Создаём тестовое оборудование
    equipment = Equipment(
        equipment_name="Тестовый прибор",
        equipment_model="TEST-001",
        equipment_type="SI",
        equipment_specs="Тестовые характеристики",
        factory_number="F12345",
        inventory_number="I12345",
        equipment_year=2025
    )
    test_db.add(equipment)
    test_db.commit()
    test_db.refresh(equipment)

    # Создаём верификацию с тестовыми данными
    verification = Verification(
        equipment_id=equipment.id,
        verification_type="verification",
        registry_number="REG-001",
        verification_interval=24,
        verification_date=date(2025, 10, 8),  # 08.10.2025
        # verification_due вычисляется автоматически БД
        verification_plan=date(2027, 10, 1),
        verification_state="state_work",
        status="status_fit"
    )
    test_db.add(verification)
    test_db.commit()
    test_db.refresh(verification)

    # Проверяем результат
    expected_due_date = date(2027, 10, 7)  # 07.10.2027
    assert verification.verification_due == expected_due_date, \
        f"Ожидалось {expected_due_date.strftime('%d.%m.%Y')}, " \
        f"получено {verification.verification_due.strftime('%d.%m.%Y')}"

    # Очистка
    test_db.delete(verification)
    test_db.delete(equipment)
    test_db.commit()


def test_verification_due_various_intervals(test_db):
    """Тест вычисления verification_due для различных интервалов."""
    test_cases = [
        # (verification_date, interval_months, expected_due_date)
        (date(2025, 10, 8), 12, date(2026, 10, 7)),  # 12 месяцев
        (date(2025, 10, 8), 24, date(2027, 10, 7)),  # 24 месяца
        (date(2025, 10, 8), 36, date(2028, 10, 7)),  # 36 месяцев
        (date(2025, 1, 31), 12, date(2026, 1, 30)),  # Граничный случай - конец месяца
    ]

    equipment = Equipment(
        equipment_name="Тестовый прибор 2",
        equipment_model="TEST-002",
        equipment_type="SI",
        factory_number="F54321",
        inventory_number="I54321",
        equipment_year=2025
    )
    test_db.add(equipment)
    test_db.commit()
    test_db.refresh(equipment)

    for ver_date, interval, expected_due in test_cases:
        verification = Verification(
            equipment_id=equipment.id,
            verification_type="calibration",
            verification_interval=interval,
            verification_date=ver_date,
            verification_plan=ver_date,
            verification_state="state_work",
            status="status_fit"
        )
        test_db.add(verification)
        test_db.commit()
        test_db.refresh(verification)

        assert verification.verification_due == expected_due, \
            f"Для даты {ver_date} и интервала {interval} мес: " \
            f"ожидалось {expected_due}, получено {verification.verification_due}"

        test_db.delete(verification)
        test_db.commit()

    # Очистка
    test_db.delete(equipment)
    test_db.commit()
