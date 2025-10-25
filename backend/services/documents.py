# deltica/backend/services/documents.py

from typing import Optional, List
from datetime import datetime
from pathlib import Path
from docxtpl import DocxTemplate
from sqlalchemy.orm import Session
from backend.app import models


class DocumentService:
    """Сервис для генерации документов из шаблонов"""

    def __init__(self, db: Session):
        self.db = db
        self.templates_dir = Path("docs/docx-templates")
        self.output_dir = Path("backend/generated_documents")
        self.output_dir.mkdir(exist_ok=True)

    def _get_equipment_full_data(self, equipment_id: int) -> Optional[dict]:
        """Получить полные данные оборудования для заполнения шаблонов"""
        equipment = self.db.query(models.Equipment).filter(
            models.Equipment.id == equipment_id
        ).first()

        if not equipment:
            return None

        # Получить связанные данные
        verification = self.db.query(models.Verification).filter(
            models.Verification.equipment_id == equipment_id
        ).first()

        responsibility = self.db.query(models.Responsibility).filter(
            models.Responsibility.equipment_id == equipment_id
        ).first()

        # Маппинг подразделений для отображения
        department_map = {
            'lbr': 'ЛБР',
            'gtl': 'ГТЛ',
            'smtsik': 'СМТСиК',
            'oks': 'ОКС',
            'oits': 'ОИТС',
            'sm': 'СМ',
            'production': 'Производство',
            'okp': 'ОКП',
            'okpnrs': 'ОКПНРС',
            'okpvrs': 'ОКПВРС',
            'lao': 'ЛАО',
            'ogt': 'ОГТ'
        }

        # Форматирование дат
        verification_date = verification.verification_date.strftime('%d.%m.%Y') if verification and verification.verification_date else ''
        verification_due = verification.verification_due.strftime('%d.%m.%Y') if verification and verification.verification_due else ''
        department = department_map.get(responsibility.department, '') if responsibility else ''

        return {
            'equipment_name': equipment.equipment_name or '',
            'equipment_model': equipment.equipment_model or '',
            'factory_number': equipment.factory_number or '',
            'inventory_number': equipment.inventory_number or '',
            'verification_date': verification_date,
            'verification_due': verification_due,
            'department': department
        }

    def generate_label(self, equipment_id: int) -> Optional[str]:
        """
        Генерировать этикетку для оборудования
        Возвращает путь к сгенерированному файлу или None при ошибке
        """
        # Получить данные оборудования
        data = self._get_equipment_full_data(equipment_id)
        if not data:
            return None

        # Загрузить шаблон
        template_path = self.templates_dir / "template_label.docx"
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон не найден: {template_path}")

        template = DocxTemplate(template_path)

        # Заполнить шаблон
        template.render(data)

        # Сохранить результат
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"label_{equipment_id}_{timestamp}.docx"
        output_path = self.output_dir / output_filename

        template.save(str(output_path))

        return str(output_path)

    def generate_labels_batch(self, equipment_ids: List[int]) -> Optional[str]:
        """
        Генерировать пакет этикеток для нескольких единиц оборудования
        Возвращает путь к сгенерированному файлу или None при ошибке
        """
        if not equipment_ids:
            return None

        # Получить данные для всех единиц оборудования
        equipments_data = []
        for equipment_id in equipment_ids:
            data = self._get_equipment_full_data(equipment_id)
            if data:  # Добавляем только найденное оборудование
                equipments_data.append(data)

        if not equipments_data:
            return None

        # Загрузить пакетный шаблон
        template_path = self.templates_dir / "template_labels_batch.docx"
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон не найден: {template_path}")

        template = DocxTemplate(template_path)

        # Заполнить шаблон
        context = {'equipments': equipments_data}
        template.render(context)

        # Сохранить результат
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"labels_batch_{len(equipments_data)}_items_{timestamp}.docx"
        output_path = self.output_dir / output_filename

        template.save(str(output_path))

        return str(output_path)
