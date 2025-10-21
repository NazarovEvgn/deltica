"""
Скрипт для проверки уникальных значений в Excel файле
"""

import sys
from pathlib import Path
import pandas as pd

# Установка кодировки для консоли Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    excel_file = project_root / "export_equipment_db.xlsx"

    if not excel_file.exists():
        print(f"Ошибка: файл {excel_file} не найден!")
        return

    print(f"Чтение данных из {excel_file}...")
    df = pd.read_excel(str(excel_file))

    print("\n=== VERIFICATION_STATE ===")
    print("Уникальные значения:")
    print(df['verification_state'].unique())
    print("\nКоличество каждого значения:")
    print(df['verification_state'].value_counts())

    print("\n=== VERIFICATION_TYPE ===")
    print("Уникальные значения:")
    print(df['verification_type'].unique())
    print("\nКоличество каждого значения:")
    print(df['verification_type'].value_counts())

    print("\n=== EQUIPMENT_TYPE ===")
    print("Уникальные значения:")
    print(df['equipment_type'].unique())
    print("\nКоличество каждого значения:")
    print(df['equipment_type'].value_counts())

if __name__ == "__main__":
    main()
