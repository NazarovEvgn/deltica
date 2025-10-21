"""
Скрипт для проверки типов данных equipment_year
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

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

    print("\nТипы данных equipment_year:")
    print(df['equipment_year'].dtype)

    print("\nВсе уникальные типы значений:")
    for val in df['equipment_year'].dropna().unique()[:30]:
        print(f"{type(val).__name__}: {val}")

    print("\nЗначения, которые выглядят как даты:")
    for idx, val in enumerate(df['equipment_year']):
        if isinstance(val, datetime):
            print(f"Строка {idx}: {val} (datetime)")
        elif pd.notna(val) and not isinstance(val, (int, float)):
            print(f"Строка {idx}: {val} (type: {type(val).__name__})")

if __name__ == "__main__":
    main()
