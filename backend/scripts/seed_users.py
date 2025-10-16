#!/usr/bin/env python3
# backend/scripts/seed_users.py
# Скрипт для создания тестовых пользователей в системе

"""
Скрипт создает тестовых пользователей для разработки и тестирования:
1. Один администратор (admin/admin123)
2. Несколько лаборантов на основе списка responsible_person из БД

Использование:
    uv run python backend/scripts/seed_users.py
"""

import sys
import io
from pathlib import Path

# Устанавливаем UTF-8 кодировку для stdout (для Windows)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.app.models import User, Responsibility
from backend.utils.auth import hash_password


def seed_users(db: Session):
    """Создает тестовых пользователей"""

    print("=" * 60)
    print("СОЗДАНИЕ ТЕСТОВЫХ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 60)

    # 1. Создаем администратора
    admin_username = "admin"
    existing_admin = db.query(User).filter(User.username == admin_username).first()

    if existing_admin:
        print(f"\n[OK] Администратор '{admin_username}' уже существует")
    else:
        admin = User(
            username=admin_username,
            password_hash=hash_password("admin123"),
            full_name="Администратор Системы",
            department="Администрация",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"\n[OK] Создан администратор:")
        print(f"   Логин: {admin_username}")
        print(f"   Пароль: admin123")
        print(f"   ФИО: Администратор Системы")
        print(f"   Роль: admin")

    # 2. Получаем список уникальных ответственных лиц и их подразделений из БД
    print("\n" + "-" * 60)
    print("СОЗДАНИЕ ЛАБОРАНТОВ НА ОСНОВЕ ДАННЫХ ИЗ БД")
    print("-" * 60)

    # Получаем уникальные комбинации responsible_person и department
    responsible_data = db.query(
        Responsibility.responsible_person,
        Responsibility.department
    ).distinct().all()

    if not responsible_data:
        print("\n[INFO] В таблице responsibility нет данных.")
        print("   Создаем тестовых лаборантов вручную...")

        # Тестовые лаборанты если в БД нет данных
        test_laborants = [
            {
                "username": "ivanov",
                "password": "lab123",
                "full_name": "Иванов Иван Иванович",
                "department": "Испытательная лаборатория",
            },
            {
                "username": "petrov",
                "password": "lab123",
                "full_name": "Петров Петр Петрович",
                "department": "Лаборатория качества",
            }
        ]

        for lab_data in test_laborants:
            existing_user = db.query(User).filter(User.username == lab_data["username"]).first()
            if existing_user:
                print(f"\n[OK] Пользователь '{lab_data['username']}' уже существует")
            else:
                laborant = User(
                    username=lab_data["username"],
                    password_hash=hash_password(lab_data["password"]),
                    full_name=lab_data["full_name"],
                    department=lab_data["department"],
                    role="laborant",
                    is_active=True
                )
                db.add(laborant)
                db.commit()
                print(f"\n[OK] Создан лаборант:")
                print(f"   Логин: {lab_data['username']}")
                print(f"   Пароль: {lab_data['password']}")
                print(f"   ФИО: {lab_data['full_name']}")
                print(f"   Подразделение: {lab_data['department']}")
                print(f"   Роль: laborant")
    else:
        print(f"\n[OK] Найдено {len(responsible_data)} уникальных ответственных лиц")

        created_count = 0
        existing_count = 0

        for person, department in responsible_data:
            if not person or not department:
                continue

            # Генерируем логин из ФИО (берем фамилию, транслитерируем)
            # Простой вариант: берем первое слово и делаем lowercase
            username = generate_username(person)

            # Проверяем существование пользователя
            existing_user = db.query(User).filter(User.username == username).first()

            if existing_user:
                existing_count += 1
                continue

            # Создаем лаборанта
            laborant = User(
                username=username,
                password_hash=hash_password("lab123"),  # Дефолтный пароль для всех
                full_name=person,
                department=department,
                role="laborant",
                is_active=True
            )
            db.add(laborant)
            db.commit()

            created_count += 1
            print(f"\n[OK] Создан лаборант:")
            print(f"   Логин: {username}")
            print(f"   Пароль: lab123")
            print(f"   ФИО: {person}")
            print(f"   Подразделение: {department}")
            print(f"   Роль: laborant")

        print(f"\n{'=' * 60}")
        print(f"ИТОГО:")
        print(f"  - Создано новых пользователей: {created_count}")
        print(f"  - Уже существовало: {existing_count}")

    # 3. Итоговая статистика
    print(f"\n{'=' * 60}")
    total_users = db.query(User).count()
    admin_count = db.query(User).filter(User.role == "admin").count()
    laborant_count = db.query(User).filter(User.role == "laborant").count()

    print("ИТОГОВАЯ СТАТИСТИКА:")
    print(f"  - Всего пользователей в системе: {total_users}")
    print(f"  - Администраторов: {admin_count}")
    print(f"  - Лаборантов: {laborant_count}")
    print("=" * 60)

    print("\n[SUCCESS] Seed завершен успешно!")
    print("\n[ВАЖНО] Все лаборанты имеют пароль: lab123")
    print("[ВАЖНО] Администратор: admin / admin123\n")


def generate_username(full_name: str) -> str:
    """
    Генерирует логин из ФИО

    Примеры:
        "Иванов Иван Иванович" -> "ivanov"
        "Петрова А.С." -> "petrova"
    """
    # Транслитерация кириллицы в латиницу (упрощенная)
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    # Берем первое слово (фамилию)
    first_word = full_name.split()[0].lower()

    # Транслитерируем
    username = ""
    for char in first_word:
        username += translit_map.get(char, char)

    # Удаляем все кроме букв и цифр
    username = ''.join(c for c in username if c.isalnum())

    return username


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_users(db)
    except Exception as e:
        print(f"\n[ERROR] Ошибка при создании пользователей: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
