#!/usr/bin/env python3
# backend/scripts/sync_users.py
# Скрипт синхронизации пользователей из конфигурационного файла с БД

"""
Скрипт читает конфигурацию пользователей из config/users_config.yaml
и синхронизирует её с базой данных:
- Создаёт новых пользователей
- Обновляет существующих (ФИО, подразделение, роль, пароль, статус активности)
- НЕ удаляет пользователей из БД (только деактивирует при is_active: false)

Использование:
    uv run python backend/scripts/sync_users.py
"""

import sys
import io
from pathlib import Path
import yaml

# Устанавливаем UTF-8 кодировку для stdout (для Windows)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.app.models import User
from backend.utils.auth import hash_password


def load_users_config(config_path: Path) -> dict:
    """Загружает конфигурацию пользователей из YAML файла"""
    if not config_path.exists():
        raise FileNotFoundError(
            f"Конфигурационный файл не найден: {config_path}\n"
            f"Создайте файл config/users_config.yaml на основе config/users_config.yaml.example"
        )

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if not config or 'users' not in config:
        raise ValueError("Некорректный формат конфига. Ожидается структура: users: [...]")

    return config


def sync_users(db: Session, users_config: list):
    """
    Синхронизирует пользователей из конфига с БД

    Args:
        db: Сессия базы данных
        users_config: Список пользователей из конфига
    """
    print("=" * 70)
    print("СИНХРОНИЗАЦИЯ ПОЛЬЗОВАТЕЛЕЙ ИЗ КОНФИГУРАЦИОННОГО ФАЙЛА")
    print("=" * 70)
    print(f"\nВсего пользователей в конфиге: {len(users_config)}")

    created_count = 0
    updated_count = 0
    errors = []

    for user_data in users_config:
        try:
            username = user_data.get('username')
            password = user_data.get('password')
            windows_username = user_data.get('windows_username')  # Опциональное поле
            full_name = user_data.get('full_name')
            department = user_data.get('department')
            role = user_data.get('role', 'laborant')
            is_active = user_data.get('is_active', True)

            # Валидация обязательных полей
            if not username:
                errors.append("Пропущен username для одного из пользователей")
                continue
            # Пароль обязателен, если не указан windows_username
            if not password and not windows_username:
                errors.append(f"Для пользователя {username} должен быть указан password или windows_username")
                continue
            if not full_name:
                errors.append(f"Пропущен full_name для пользователя {username}")
                continue
            if not department:
                errors.append(f"Пропущен department для пользователя {username}")
                continue
            if role not in ['admin', 'laborant']:
                errors.append(f"Некорректная роль '{role}' для пользователя {username}. Допустимо: admin, laborant")
                continue

            # Проверяем существование пользователя
            existing_user = db.query(User).filter(User.username == username).first()

            if existing_user:
                # Обновляем существующего пользователя
                print(f"\n[UPDATE] Обновление пользователя '{username}':")

                # Сравниваем и обновляем поля
                changes = []

                if existing_user.full_name != full_name:
                    changes.append(f"  ФИО: '{existing_user.full_name}' -> '{full_name}'")
                    existing_user.full_name = full_name

                if existing_user.department != department:
                    changes.append(f"  Подразделение: '{existing_user.department}' -> '{department}'")
                    existing_user.department = department

                if existing_user.role != role:
                    changes.append(f"  Роль: '{existing_user.role}' -> '{role}'")
                    existing_user.role = role

                if existing_user.is_active != is_active:
                    changes.append(f"  Активен: {existing_user.is_active} -> {is_active}")
                    existing_user.is_active = is_active

                # Обновляем windows_username
                if existing_user.windows_username != windows_username:
                    changes.append(f"  Windows username: '{existing_user.windows_username}' -> '{windows_username}'")
                    existing_user.windows_username = windows_username

                # Пароль обновляем только если указан в конфиге
                if password:
                    new_hash = hash_password(password)
                    existing_user.password_hash = new_hash
                    changes.append("  Пароль: обновлён")
                elif not windows_username and not existing_user.password_hash:
                    # Если нет ни пароля, ни windows_username - это ошибка
                    errors.append(f"Пользователь {username} не имеет ни пароля, ни windows_username")
                    continue

                if changes:
                    for change in changes:
                        print(change)
                    db.commit()
                    updated_count += 1
                else:
                    print("  Без изменений")

            else:
                # Создаём нового пользователя
                new_user = User(
                    username=username,
                    password_hash=hash_password(password) if password else None,
                    windows_username=windows_username,
                    full_name=full_name,
                    department=department,
                    role=role,
                    is_active=is_active
                )
                db.add(new_user)
                db.commit()

                print(f"\n[CREATE] Создан пользователь:")
                print(f"  Логин: {username}")
                print(f"  ФИО: {full_name}")
                print(f"  Подразделение: {department}")
                print(f"  Роль: {role}")
                print(f"  Активен: {is_active}")
                if windows_username:
                    print(f"  Windows username: {windows_username}")
                if password:
                    print(f"  Аутентификация: пароль")
                else:
                    print(f"  Аутентификация: Windows SSO")

                created_count += 1

        except Exception as e:
            errors.append(f"Ошибка при обработке пользователя {user_data.get('username', 'unknown')}: {e}")
            continue

    # Итоги
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ СИНХРОНИЗАЦИИ:")
    print(f"  - Создано новых пользователей: {created_count}")
    print(f"  - Обновлено существующих: {updated_count}")
    print(f"  - Ошибок: {len(errors)}")

    if errors:
        print("\n[ОШИБКИ]")
        for error in errors:
            print(f"  - {error}")

    # Итоговая статистика из БД
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_count = db.query(User).filter(User.role == "admin").count()
    laborant_count = db.query(User).filter(User.role == "laborant").count()

    print("\nИТОГОВАЯ СТАТИСТИКА (БД):")
    print(f"  - Всего пользователей: {total_users}")
    print(f"  - Активных: {active_users}")
    print(f"  - Администраторов: {admin_count}")
    print(f"  - Лаборантов: {laborant_count}")
    print("=" * 70)

    if errors:
        print("\n[WARNING] Синхронизация завершена с ошибками")
    else:
        print("\n[SUCCESS] Синхронизация завершена успешно!")


def main():
    """Главная функция"""
    # Путь к конфигурационному файлу
    config_path = project_root / "config" / "users_config.yaml"

    try:
        # Загружаем конфигурацию
        print(f"Загрузка конфигурации из: {config_path}")
        config = load_users_config(config_path)
        users_config = config['users']

        # Синхронизируем с БД
        db = SessionLocal()
        try:
            sync_users(db, users_config)
        finally:
            db.close()

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
