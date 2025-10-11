# deltica/backend/tests/test_status_calculation.py

import pytest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from backend.services.main_table import calculate_status


def test_status_expired():
    """Тест: status = 'status_expired' если текущая дата > verification_due."""
    today = date.today()
    past_due_date = today - timedelta(days=10)  # verification_due 10 дней назад

    status = calculate_status(
        verification_due=past_due_date,
        verification_state="state_work"
    )

    assert status == "status_expired", f"Expected 'status_expired', got '{status}'"


def test_status_expiring_14_days():
    """Тест: status = 'status_expiring' если до verification_due осталось 14 дней."""
    today = date.today()
    due_date = today + timedelta(days=14)  # verification_due через 14 дней

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_work"
    )

    assert status == "status_expiring", f"Expected 'status_expiring', got '{status}'"


def test_status_expiring_10_days():
    """Тест: status = 'status_expiring' если до verification_due осталось 10 дней."""
    today = date.today()
    due_date = today + timedelta(days=10)  # verification_due через 10 дней

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_work"
    )

    assert status == "status_expiring", f"Expected 'status_expiring', got '{status}'"


def test_status_expiring_1_day():
    """Тест: status = 'status_expiring' если до verification_due остался 1 день."""
    today = date.today()
    due_date = today + timedelta(days=1)  # verification_due завтра

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_work"
    )

    assert status == "status_expiring", f"Expected 'status_expiring', got '{status}'"


def test_status_duplicates_state_work():
    """Тест: status дублирует verification_state = 'state_work' -> 'status_fit'."""
    today = date.today()
    due_date = today + timedelta(days=30)  # verification_due через 30 дней (> 14)

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_work"
    )

    assert status == "status_fit", f"Expected 'status_fit', got '{status}'"


def test_status_duplicates_state_storage():
    """Тест: status дублирует verification_state = 'state_storage' -> 'status_storage'."""
    today = date.today()
    due_date = today + timedelta(days=30)

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_storage"
    )

    assert status == "status_storage", f"Expected 'status_storage', got '{status}'"


def test_status_duplicates_state_verification():
    """Тест: status дублирует verification_state = 'state_verification' -> 'status_verification'."""
    today = date.today()
    due_date = today + timedelta(days=30)

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_verification"
    )

    assert status == "status_verification", f"Expected 'status_verification', got '{status}'"


def test_status_duplicates_state_repair():
    """Тест: status дублирует verification_state = 'state_repair' -> 'status_repair'."""
    today = date.today()
    due_date = today + timedelta(days=30)

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_repair"
    )

    assert status == "status_repair", f"Expected 'status_repair', got '{status}'"


def test_status_duplicates_state_archived():
    """Тест: status дублирует verification_state = 'state_archived' -> 'status_fit'."""
    today = date.today()
    due_date = today + timedelta(days=30)

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_archived"
    )

    assert status == "status_fit", f"Expected 'status_fit', got '{status}'"


def test_status_storage_ignores_expiration():
    """Тест: state_storage дублируется независимо от срока (даже если просрочен)."""
    today = date.today()
    past_due_date = today - timedelta(days=5)  # Срок истек 5 дней назад

    # Но оборудование на хранении, поэтому status = status_storage
    status = calculate_status(
        verification_due=past_due_date,
        verification_state="state_storage"
    )

    assert status == "status_storage", f"Expected 'status_storage', got '{status}'"


def test_status_repair_ignores_expiration():
    """Тест: state_repair дублируется независимо от срока (даже если истекает)."""
    today = date.today()
    due_date = today + timedelta(days=7)  # 7 дней до истечения (< 14)

    # Но оборудование на ремонте, поэтому status = status_repair
    status = calculate_status(
        verification_due=due_date,
        verification_state="state_repair"
    )

    assert status == "status_repair", f"Expected 'status_repair', got '{status}'"


def test_status_verification_ignores_expiration():
    """Тест: state_verification дублируется независимо от срока."""
    today = date.today()
    past_due_date = today - timedelta(days=30)  # Сильно просрочен

    # Но оборудование на верификации, поэтому status = status_verification
    status = calculate_status(
        verification_due=past_due_date,
        verification_state="state_verification"
    )

    assert status == "status_verification", f"Expected 'status_verification', got '{status}'"


def test_status_boundary_15_days():
    """Тест: граничное условие - 15 дней до истечения должно быть status_fit."""
    today = date.today()
    due_date = today + timedelta(days=15)  # Ровно 15 дней

    status = calculate_status(
        verification_due=due_date,
        verification_state="state_work"
    )

    # 15 дней > 14, значит status_fit
    assert status == "status_fit", f"Expected 'status_fit' for 15 days, got '{status}'"
