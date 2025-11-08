"""
Скрипт для выполнения SQL импорта данных из import_new_data.sql в PostgreSQL
"""

import sys
from pathlib import Path

# Установка кодировки для консоли Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.core.database import engine


def execute_sql_file(sql_file_path: str):
    """Выполняет SQL скрипт из файла"""
    print(f"Чтение SQL скрипта из {sql_file_path}...")

    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print(f"Размер SQL скрипта: {len(sql_content)} символов\n")

    # Выполняем весь SQL скрипт целиком
    with engine.connect() as connection:
        print("Начало транзакции...")
        trans = connection.begin()

        try:
            # Выполняем весь SQL скрипт за раз
            connection.execute(text(sql_content))

            trans.commit()
            print(f"\n✅ SQL скрипт успешно выполнен!")
            print("Транзакция зафиксирована.")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ Ошибка при выполнении SQL скрипта:")
            print(f"Ошибка: {e}")
            print("\nТранзакция отменена.")
            raise


def main():
    sql_file = project_root / "import_new_data.sql"

    if not sql_file.exists():
        print(f"❌ Ошибка: SQL файл {sql_file} не найден!")
        print("Сначала запустите: uv run python backend/scripts/import_new_data.py")
        return

    print("=" * 80)
    print("ИМПОРТ ДАННЫХ ИЗ 'import data.xlsx' В БАЗУ ДАННЫХ")
    print("=" * 80)
    print("\n⚠️  ВНИМАНИЕ: Этот скрипт удалит ВСЕ существующие данные оборудования!")
    print("⚠️  Будут очищены таблицы: equipment, verification, responsibility, finance")
    print("\nПродолжить? (yes/no): ", end='')

    response = input().strip().lower()

    if response != 'yes':
        print("\n❌ Импорт отменен.")
        return

    print("\nНачинаем импорт...\n")
    execute_sql_file(str(sql_file))

    print("\n" + "=" * 80)
    print("✅ ИМПОРТ ЗАВЕРШЕН УСПЕШНО")
    print("=" * 80)
    print("\nИмпортировано записей из файла 'import data.xlsx'")
    print("Проверьте данные в приложении или через pgAdmin4.")


if __name__ == "__main__":
    main()
