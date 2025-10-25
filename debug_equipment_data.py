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

# Создаём сервис
service = DocumentService(db)

# Получаем данные для ID 1353
print("=== Данные для ID 1353 ===")
data = service._get_equipment_full_data(1353)

if data:
    print("✓ Данные найдены:")
    for key, value in data.items():
        print(f"  {key}: {value}")
else:
    print("✗ Данные не найдены (None)")

db.close()
