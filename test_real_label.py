import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.services.documents import DocumentService
from backend.core.config import settings

# Подключение к БД
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Тестовая генерация для Конуса Васильева (ID 1353)
service = DocumentService(db)

print("=== Тест генерации одной этикетки ===")
print("ID оборудования: 1353 (Конус Васильева)")

# Генерируем этикетку
try:
    file_path = service.generate_labels_batch([1353])
except Exception as e:
    print(f"✗ Исключение при генерации: {e}")
    import traceback
    traceback.print_exc()
    file_path = None

if file_path:
    print(f"✓ Файл сгенерирован: {file_path}")

    # Проверяем содержимое
    from docx import Document
    doc = Document(file_path)
    table = doc.tables[0]

    print("\n=== Содержимое этикетки ===")
    print(f"Название: {table.rows[0].cells[0].text.strip()}")
    print(f"Зав. №: {table.rows[1].cells[2].text.strip()}")
    print(f"Инв. №: {table.rows[2].cells[2].text.strip()}")
    print(f"Дата с: {table.rows[4].cells[1].text.strip()}")
    print(f"Дата по: {table.rows[5].cells[1].text.strip()}")
    print(f"ТФ ГПП: {table.rows[4].cells[3].text.strip()}")
    print(f"Подразделение: {table.rows[5].cells[3].text.strip()}")
else:
    print("✗ Ошибка при генерации")

db.close()
