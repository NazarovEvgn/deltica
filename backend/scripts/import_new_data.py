"""
Скрипт для импорта данных оборудования из Excel файла 'import data.xlsx'
Создает SQL скрипт для очистки и импорта данных в PostgreSQL
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Установка кодировки для консоли Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def read_excel_data(file_path: str) -> pd.DataFrame:
    """Читает данные из Excel файла"""
    print(f"Чтение данных из {file_path}...")
    df = pd.read_excel(file_path)

    # Исправляем опечатку в названии колонки
    if 'equipmnet_model' in df.columns:
        df.rename(columns={'equipmnet_model': 'equipment_model'}, inplace=True)
        print("⚠️  Исправлена опечатка: equipmnet_model → equipment_model")

    print(f"Загружено {len(df)} строк")
    print(f"Колонки: {list(df.columns)}")
    return df


def escape_sql_string(value) -> str:
    """Экранирует строку для SQL"""
    if pd.isna(value) or value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return "NULL"
        return str(value)
    if isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d')}'"
    # Проверяем, если это строка с некорректной датой
    if isinstance(value, str):
        # Проверяем на паттерн даты с запятой вместо точки (07.05,2025 -> 07.05.2025)
        if ',' in value and len(value.split('.')) >= 2:
            value = value.replace(',', '.')
            # Пытаемся распарсить как дату
            try:
                from datetime import datetime as dt
                date_obj = dt.strptime(value, '%d.%m.%Y')
                return f"'{date_obj.strftime('%Y-%m-%d')}'"
            except:
                pass  # Если не получилось, обрабатываем как обычную строку
    # Строка - экранируем одинарные кавычки
    value = str(value).replace("'", "''")
    return f"'{value}'"


# Маппинг значений из Excel в значения БД
VERIFICATION_TYPE_MAP = {
    'поверка': 'verification',
    'калибровка': 'calibration',
    'аттестация': 'certification'
}

VERIFICATION_STATE_MAP = {
    'в работе': 'state_work',
    'на хранении': 'state_storage',
    'на консервации': 'state_storage',
    'на поверке': 'state_verification',
    'на верификации': 'state_verification',
    'в ремонте': 'state_repair',
    'архив': 'state_archived'
}

EQUIPMENT_TYPE_MAP = {
    'СИ': 'SI',
    'ИО': 'IO'
}

DEPARTMENT_MAP = {
    'Группа СМ': 'gruppa_sm',
    'ГТЛ': 'gtl',
    'ЛБР': 'lbr',
    'ЛТР': 'ltr',
    'ЛХАиЭИ': 'lhaiei',
    'ОГМК': 'ogmk',
    'ОИИ': 'oii',
    'ОООПС': 'ooops',
    'СМТСиК': 'smtsik',
    'СОИИ': 'soii',
    'ТО': 'to',
    'ТС': 'ts',
    'ЭС': 'es'
}


def map_value(value, mapping):
    """Маппит значение через словарь"""
    if pd.isna(value) or value is None:
        return None
    return mapping.get(str(value).strip(), str(value))


def generate_sql_script(df: pd.DataFrame, output_file: str):
    """Генерирует SQL скрипт для импорта данных"""
    print(f"\nГенерация SQL скрипта...")

    sql_lines = []

    # Заголовок
    sql_lines.append("-- SQL скрипт для импорта данных оборудования из 'import data.xlsx'")
    sql_lines.append(f"-- Создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_lines.append(f"-- Количество записей: {len(df)}\n")

    # Очистка существующих данных
    sql_lines.append("-- Очистка существующих данных")
    sql_lines.append("DELETE FROM equipment_files;")
    sql_lines.append("DELETE FROM finance;")
    sql_lines.append("DELETE FROM responsibility;")
    sql_lines.append("DELETE FROM verification;")
    sql_lines.append("DELETE FROM equipment;")
    sql_lines.append("-- Сброс последовательностей")
    sql_lines.append("ALTER SEQUENCE equipment_id_seq RESTART WITH 1;")
    sql_lines.append("ALTER SEQUENCE verification_id_seq RESTART WITH 1;")
    sql_lines.append("ALTER SEQUENCE responsibility_id_seq RESTART WITH 1;")
    sql_lines.append("ALTER SEQUENCE finance_id_seq RESTART WITH 1;\n")

    # Импорт данных
    sql_lines.append("-- Импорт данных оборудования\n")

    for idx, row in df.iterrows():
        equipment_id = idx + 1  # ID начинается с 1

        # Маппинг значений
        equipment_type = map_value(row.get('equipment_type'), EQUIPMENT_TYPE_MAP) or 'SI'
        verification_type = map_value(row.get('verification_type'), VERIFICATION_TYPE_MAP) or 'verification'
        verification_state = map_value(row.get('verification_state'), VERIFICATION_STATE_MAP) or 'state_work'

        # Определяем статус на основе состояния (статус будет вычислен триггером БД)
        status = 'status_fit'

        # Equipment (с обработкой NULL значений)
        equipment_year = row.get('equipment_year')
        if pd.isna(equipment_year) or equipment_year is None:
            equipment_year = 2000
        elif isinstance(equipment_year, datetime):
            equipment_year = equipment_year.year

        # Если equipment_model NULL, используем equipment_name
        equipment_model = row.get('equipment_model')
        if pd.isna(equipment_model) or equipment_model is None or equipment_model == '':
            equipment_model = row.get('equipment_name', 'Неизвестно')

        # Если factory_number NULL, используем дефолт
        factory_number = row.get('factory_number')
        if pd.isna(factory_number) or factory_number is None or factory_number == '':
            factory_number = f'н/д-{equipment_id}'

        # Если inventory_number NULL, используем дефолт
        inventory_number = row.get('inventory_number')
        if pd.isna(inventory_number) or inventory_number is None or inventory_number == '':
            inventory_number = f'н/д-{equipment_id}'

        sql_lines.append(f"-- Запись {equipment_id}")
        sql_lines.append(
            f"INSERT INTO equipment (id, equipment_name, equipment_model, equipment_type, "
            f"equipment_specs, factory_number, inventory_number, equipment_year) VALUES ("
            f"{equipment_id}, "
            f"{escape_sql_string(row.get('equipment_name'))}, "
            f"{escape_sql_string(equipment_model)}, "
            f"{escape_sql_string(equipment_type)}, "
            f"{escape_sql_string(row.get('equipment_specs'))}, "
            f"{escape_sql_string(factory_number)}, "
            f"{escape_sql_string(inventory_number)}, "
            f"{escape_sql_string(equipment_year)});"
        )

        # Verification (с обработкой NULL значений)
        verification_date = row.get('verification_date')
        verification_plan = row.get('verification_plan')
        verification_interval = row.get('verification_interval')

        # Если verification_date NULL, устанавливаем текущую дату
        if pd.isna(verification_date) or verification_date is None:
            from datetime import date as dt_date
            verification_date = dt_date.today()

        # Если verification_plan NULL, вычисляем его
        if pd.isna(verification_plan) or verification_plan is None:
            if not pd.isna(verification_date) and verification_date is not None and not pd.isna(verification_interval):
                from dateutil.relativedelta import relativedelta
                verification_plan = verification_date + relativedelta(months=int(verification_interval))

        sql_lines.append(
            f"INSERT INTO verification (equipment_id, verification_type, registry_number, "
            f"verification_interval, verification_date, verification_plan, "
            f"verification_state, status) VALUES ("
            f"{equipment_id}, "
            f"{escape_sql_string(verification_type)}, "
            f"{escape_sql_string(row.get('registry_number'))}, "
            f"{escape_sql_string(verification_interval)}, "
            f"{escape_sql_string(verification_date)}, "
            f"{escape_sql_string(verification_plan)}, "
            f"{escape_sql_string(verification_state)}, "
            f"{escape_sql_string(status)});"
        )

        # Responsibility (с маппингом department)
        department = map_value(row.get('department'), DEPARTMENT_MAP)
        if not department:
            department = row.get('department', 'oii')

        sql_lines.append(
            f"INSERT INTO responsibility (equipment_id, department, responsible_person, "
            f"verifier_org) VALUES ("
            f"{equipment_id}, "
            f"{escape_sql_string(department)}, "
            f"{escape_sql_string(row.get('responsible_person'))}, "
            f"{escape_sql_string(row.get('verifier_org'))});"
        )

        # Finance (с обработкой NULL значений и вычислением total_cost)
        budget_item = row.get('budget_item')
        if pd.isna(budget_item) or budget_item is None:
            budget_item = '00.00.00.0'

        quantity = row.get('quantity')
        if pd.isna(quantity) or quantity is None:
            quantity = 1

        coefficient = row.get('coefficient')
        if pd.isna(coefficient) or coefficient is None:
            coefficient = 1.0

        cost_rate = row.get('cost_rate')

        # Вычисляем total_cost
        total_cost = None
        if not pd.isna(cost_rate) and cost_rate is not None:
            total_cost = float(cost_rate) * float(quantity) * float(coefficient)

        sql_lines.append(
            f"INSERT INTO finance (equipment_model_id, budget_item, code_rate, cost_rate, "
            f"quantity, coefficient, total_cost, invoice_number, paid_amount, payment_date) VALUES ("
            f"{equipment_id}, "
            f"{escape_sql_string(budget_item)}, "
            f"{escape_sql_string(row.get('code_rate'))}, "
            f"{escape_sql_string(cost_rate)}, "
            f"{escape_sql_string(quantity)}, "
            f"{escape_sql_string(coefficient)}, "
            f"{escape_sql_string(total_cost)}, "
            f"{escape_sql_string(row.get('invoice_number'))}, "
            f"{escape_sql_string(row.get('paid_amount'))}, "
            f"{escape_sql_string(row.get('payment_date'))});\n"
        )

    # Обновление последовательностей
    sql_lines.append("-- Обновление последовательностей до следующего доступного значения")
    sql_lines.append(f"SELECT setval('equipment_id_seq', {len(df)});")
    sql_lines.append(f"SELECT setval('verification_id_seq', {len(df)});")
    sql_lines.append(f"SELECT setval('responsibility_id_seq', {len(df)});")
    sql_lines.append(f"SELECT setval('finance_id_seq', {len(df)});")

    # Запись в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))

    print(f"✅ SQL скрипт сохранен в {output_file}")
    print(f"Всего команд: {len(sql_lines)}")


def main():
    excel_file = project_root / "import data.xlsx"
    output_sql = project_root / "import_new_data.sql"

    if not excel_file.exists():
        print(f"❌ Ошибка: файл {excel_file} не найден!")
        return

    # Читаем данные
    df = read_excel_data(str(excel_file))

    # Генерируем SQL
    generate_sql_script(df, str(output_sql))

    print("\n" + "="*80)
    print("✅ Готово!")
    print("="*80)
    print(f"\nСоздан SQL скрипт: {output_sql}")
    print(f"Записей для импорта: {len(df)}")
    print("\nДля выполнения импорта запустите следующую команду:")
    print(f"  uv run python backend/scripts/execute_import_sql.py")


if __name__ == "__main__":
    main()
