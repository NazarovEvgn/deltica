# deltica/backend/services/archive.py

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app import models


class ArchiveService:
    """Сервис для работы с архивом оборудования"""

    def __init__(self, db: Session):
        self.db = db

    def archive_equipment(self, equipment_id: int, archive_reason: Optional[str] = None) -> Optional[models.ArchivedEquipment]:
        """
        Архивировать оборудование: скопировать в архивные таблицы и удалить из основных
        """
        # Получить оборудование со всеми связанными данными
        equipment = self.db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
        if not equipment:
            return None

        # Получить связанные данные
        verification = self.db.query(models.Verification).filter(
            models.Verification.equipment_id == equipment_id
        ).first()

        responsibility = self.db.query(models.Responsibility).filter(
            models.Responsibility.equipment_id == equipment_id
        ).first()

        finance = self.db.query(models.Finance).filter(
            models.Finance.equipment_model_id == equipment_id
        ).first()

        files = self.db.query(models.EquipmentFile).filter(
            models.EquipmentFile.equipment_id == equipment_id
        ).all()

        # 1. Создать запись в archived_equipment
        archived_equipment = models.ArchivedEquipment(
            original_id=equipment.id,
            equipment_name=equipment.equipment_name,
            equipment_model=equipment.equipment_model,
            equipment_type=equipment.equipment_type,
            equipment_specs=equipment.equipment_specs,
            factory_number=equipment.factory_number,
            inventory_number=equipment.inventory_number,
            equipment_year=equipment.equipment_year,
            archive_reason=archive_reason,
            archived_at=datetime.utcnow()
        )
        self.db.add(archived_equipment)
        self.db.flush()  # Получить ID для связанных записей

        # 2. Скопировать verification
        if verification:
            archived_verification = models.ArchivedVerification(
                archived_equipment_id=archived_equipment.id,
                original_equipment_id=equipment_id,
                verification_type=verification.verification_type,
                registry_number=verification.registry_number,
                verification_interval=verification.verification_interval,
                verification_date=verification.verification_date,
                verification_due=verification.verification_due,  # Копируем computed значение
                verification_plan=verification.verification_plan,
                verification_state=verification.verification_state,
                status=verification.status
            )
            self.db.add(archived_verification)

        # 3. Скопировать responsibility
        if responsibility:
            archived_responsibility = models.ArchivedResponsibility(
                archived_equipment_id=archived_equipment.id,
                original_equipment_id=equipment_id,
                department=responsibility.department,
                responsible_person=responsibility.responsible_person,
                verifier_org=responsibility.verifier_org
            )
            self.db.add(archived_responsibility)

        # 4. Скопировать finance
        if finance:
            archived_finance = models.ArchivedFinance(
                archived_equipment_id=archived_equipment.id,
                original_equipment_id=equipment_id,
                cost_rate=finance.cost_rate,
                quantity=finance.quantity,
                coefficient=finance.coefficient,
                total_cost=finance.total_cost,
                invoice_number=finance.invoice_number,
                paid_amount=finance.paid_amount,
                payment_date=finance.payment_date
            )
            self.db.add(archived_finance)

        # 5. Скопировать files
        for file in files:
            archived_file = models.ArchivedEquipmentFile(
                archived_equipment_id=archived_equipment.id,
                original_equipment_id=equipment_id,
                file_name=file.file_name,
                file_path=file.file_path,
                file_type=file.file_type,
                file_size=file.file_size,
                uploaded_at=file.uploaded_at
            )
            self.db.add(archived_file)

        # 6. Явно удалить связанные записи (ForeignKey не имеет CASCADE на уровне БД)
        if verification:
            self.db.delete(verification)
        if responsibility:
            self.db.delete(responsibility)
        if finance:
            self.db.delete(finance)
        for file in files:
            self.db.delete(file)

        # 7. Удалить оригинальное оборудование
        self.db.delete(equipment)

        # Commit всех изменений
        self.db.commit()
        self.db.refresh(archived_equipment)

        return archived_equipment

    def get_all_archived(self) -> List[models.ArchivedEquipment]:
        """Получить все архивные записи"""
        return self.db.query(models.ArchivedEquipment).all()

    def get_archived_by_id(self, archived_equipment_id: int) -> Optional[models.ArchivedEquipment]:
        """Получить архивную запись по ID"""
        return self.db.query(models.ArchivedEquipment).filter(
            models.ArchivedEquipment.id == archived_equipment_id
        ).first()

    def restore_equipment(self, archived_equipment_id: int) -> Optional[models.Equipment]:
        """
        Восстановить оборудование из архива: скопировать обратно в основные таблицы и удалить из архива
        """
        # Получить архивную запись со всеми связанными данными
        archived_equipment = self.db.query(models.ArchivedEquipment).filter(
            models.ArchivedEquipment.id == archived_equipment_id
        ).first()

        if not archived_equipment:
            return None

        # Получить связанные архивные данные
        archived_verification = self.db.query(models.ArchivedVerification).filter(
            models.ArchivedVerification.archived_equipment_id == archived_equipment_id
        ).first()

        archived_responsibility = self.db.query(models.ArchivedResponsibility).filter(
            models.ArchivedResponsibility.archived_equipment_id == archived_equipment_id
        ).first()

        archived_finance = self.db.query(models.ArchivedFinance).filter(
            models.ArchivedFinance.archived_equipment_id == archived_equipment_id
        ).first()

        archived_files = self.db.query(models.ArchivedEquipmentFile).filter(
            models.ArchivedEquipmentFile.archived_equipment_id == archived_equipment_id
        ).all()

        # 1. Восстановить equipment
        equipment = models.Equipment(
            equipment_name=archived_equipment.equipment_name,
            equipment_model=archived_equipment.equipment_model,
            equipment_type=archived_equipment.equipment_type,
            equipment_specs=archived_equipment.equipment_specs,
            factory_number=archived_equipment.factory_number,
            inventory_number=archived_equipment.inventory_number,
            equipment_year=archived_equipment.equipment_year
        )
        self.db.add(equipment)
        self.db.flush()  # Получить новый ID

        # 2. Восстановить verification
        if archived_verification:
            verification = models.Verification(
                equipment_id=equipment.id,
                verification_type=archived_verification.verification_type,
                registry_number=archived_verification.registry_number,
                verification_interval=archived_verification.verification_interval,
                verification_date=archived_verification.verification_date,
                # verification_due будет вычислено автоматически (computed column)
                verification_plan=archived_verification.verification_plan,
                verification_state=archived_verification.verification_state,
                status=archived_verification.status
            )
            self.db.add(verification)

        # 3. Восстановить responsibility
        if archived_responsibility:
            responsibility = models.Responsibility(
                equipment_id=equipment.id,
                department=archived_responsibility.department,
                responsible_person=archived_responsibility.responsible_person,
                verifier_org=archived_responsibility.verifier_org
            )
            self.db.add(responsibility)

        # 4. Восстановить finance
        if archived_finance:
            finance = models.Finance(
                equipment_model_id=equipment.id,
                cost_rate=archived_finance.cost_rate,
                quantity=archived_finance.quantity,
                coefficient=archived_finance.coefficient,
                total_cost=archived_finance.total_cost,
                invoice_number=archived_finance.invoice_number,
                paid_amount=archived_finance.paid_amount,
                payment_date=archived_finance.payment_date
            )
            self.db.add(finance)

        # 5. Восстановить files
        for archived_file in archived_files:
            file = models.EquipmentFile(
                equipment_id=equipment.id,
                file_name=archived_file.file_name,
                file_path=archived_file.file_path,
                file_type=archived_file.file_type,
                file_size=archived_file.file_size,
                uploaded_at=archived_file.uploaded_at
            )
            self.db.add(file)

        # 6. Явно удалить архивные связанные записи
        if archived_verification:
            self.db.delete(archived_verification)
        if archived_responsibility:
            self.db.delete(archived_responsibility)
        if archived_finance:
            self.db.delete(archived_finance)
        for archived_file in archived_files:
            self.db.delete(archived_file)

        # 7. Удалить архивное оборудование
        self.db.delete(archived_equipment)

        # Commit всех изменений
        self.db.commit()
        self.db.refresh(equipment)

        return equipment

    def delete_archived(self, archived_equipment_id: int) -> bool:
        """Удалить архивную запись навсегда"""
        archived_equipment = self.db.query(models.ArchivedEquipment).filter(
            models.ArchivedEquipment.id == archived_equipment_id
        ).first()

        if not archived_equipment:
            return False

        self.db.delete(archived_equipment)
        self.db.commit()
        return True
