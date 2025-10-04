# deltica/backend/services/main_table.py

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from backend.app.models import Equipment, Verification, Responsibility, Finance
from backend.app.schemas import MainTableResponse, MainTableCreate, MainTableUpdate


class MainTableService:

    def __init__(self, db: Session):
        self.db = db

    def get_all_data(self) -> List[MainTableResponse]:
        """
        Получить все данные из всех таблиц с JOIN
        """
        query = (
            select(
                Equipment.id.label("equipment_id"),
                Equipment.equipment_name,
                Equipment.equipment_model,
                Equipment.factory_number,
                Equipment.inventory_number,
                Verification.verification_type,
                Verification.verification_interval,
                Verification.verification_date,
                Verification.verification_due,
                Verification.verification_plan,
                Verification.verification_state,
                Verification.status,
                Responsibility.department,
                Responsibility.responsible_person,
                Responsibility.verifier_org
            )
            .select_from(Equipment)
            .join(Verification, Equipment.id == Verification.equipment_id, isouter=True)
            .join(Responsibility, Equipment.id == Responsibility.equipment_id, isouter=True)
        )

        result = self.db.execute(query).fetchall()

        # Преобразование результата в список схем
        return [
            MainTableResponse(
                equipment_id=row.equipment_id,
                equipment_name=row.equipment_name,
                equipment_model=row.equipment_model,
                factory_number=row.factory_number,
                inventory_number=row.inventory_number,
                verification_type=row.verification_type or "",
                verification_interval=row.verification_interval or 0,
                verification_date=row.verification_date,
                verification_due=row.verification_due,
                verification_plan=row.verification_plan,
                verification_state=row.verification_state or "",
                status=row.status or "",
                department=row.department,
                responsible_person=row.responsible_person,
                verifier_org=row.verifier_org
            )
            for row in result
        ]

    def create_equipment_full(self, data: MainTableCreate) -> MainTableResponse:
        """
        Создать новое оборудование со всеми связанными данными
        """
        # Создаем оборудование
        equipment = Equipment(
            equipment_name=data.equipment_name,
            equipment_model=data.equipment_model,
            equipment_type=data.equipment_type,
            equipment_specs=data.equipment_specs,
            factory_number=data.factory_number,
            inventory_number=data.inventory_number,
            equipment_year=data.equipment_year
        )

        self.db.add(equipment)
        self.db.flush()  # Получаем ID оборудования

        # Создаем верификацию
        verification = Verification(
            equipment_id=equipment.id,
            verification_type=data.verification_type,
            registry_number=data.registry_number,
            verification_interval=data.verification_interval,
            verification_date=data.verification_date,
            verification_due=data.verification_due,
            verification_plan=data.verification_plan,
            verification_state=data.verification_state,
            status=data.status
        )

        self.db.add(verification)

        # Создаем ответственность
        responsibility = Responsibility(
            equipment_id=equipment.id,
            department=data.department,
            responsible_person=data.responsible_person,
            verifier_org=data.verifier_org
        )

        self.db.add(responsibility)

        # Создаем финансы
        finance = Finance(
            equipment_model_id=equipment.id,
            cost_rate=data.cost_rate,
            quantity=data.quantity,
            coefficient=data.coefficient,
            total_cost=data.total_cost,
            invoice_number=data.invoice_number,
            paid_amount=data.paid_amount,
            payment_date=data.payment_date
        )

        self.db.add(finance)
        self.db.commit()

        # Возвращаем созданные данные
        return MainTableResponse(
            equipment_id=equipment.id,
            equipment_name=equipment.equipment_name,
            equipment_model=equipment.equipment_model,
            factory_number=equipment.factory_number,
            inventory_number=equipment.inventory_number,
            verification_type=verification.verification_type,
            verification_interval=verification.verification_interval,
            verification_date=verification.verification_date,
            verification_due=verification.verification_due,
            verification_plan=verification.verification_plan,
            verification_state=verification.verification_state,
            status=verification.status,
            department=responsibility.department,
            responsible_person=responsibility.responsible_person,
            verifier_org=responsibility.verifier_org
        )

    def update_equipment_full(self, equipment_id: int, data: MainTableUpdate) -> Optional[MainTableResponse]:
        """
        Обновить оборудование со всеми связанными данными
        """
        equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
        if not equipment:
            return None

        # Обновляем оборудование
        equipment.equipment_name = data.equipment_name
        equipment.equipment_model = data.equipment_model
        equipment.equipment_type = data.equipment_type
        equipment.equipment_specs = data.equipment_specs
        equipment.factory_number = data.factory_number
        equipment.inventory_number = data.inventory_number
        equipment.equipment_year = data.equipment_year

        # Обновляем верификацию
        verification = self.db.query(Verification).filter(Verification.equipment_id == equipment_id).first()
        if verification:
            verification.verification_type = data.verification_type
            verification.registry_number = data.registry_number
            verification.verification_interval = data.verification_interval
            verification.verification_date = data.verification_date
            verification.verification_due = data.verification_due
            verification.verification_plan = data.verification_plan
            verification.verification_state = data.verification_state
            verification.status = data.status

        # Обновляем ответственность
        responsibility = self.db.query(Responsibility).filter(Responsibility.equipment_id == equipment_id).first()
        if responsibility:
            responsibility.department = data.department
            responsibility.responsible_person = data.responsible_person
            responsibility.verifier_org = data.verifier_org

        # Обновляем финансы
        finance = self.db.query(Finance).filter(Finance.equipment_model_id == equipment_id).first()
        if finance:
            finance.cost_rate = data.cost_rate
            finance.quantity = data.quantity
            finance.coefficient = data.coefficient
            finance.total_cost = data.total_cost
            finance.invoice_number = data.invoice_number
            finance.paid_amount = data.paid_amount
            finance.payment_date = data.payment_date

        self.db.commit()

        # Возвращаем обновленные данные
        return MainTableResponse(
            equipment_id=equipment.id,
            equipment_name=equipment.equipment_name,
            equipment_model=equipment.equipment_model,
            factory_number=equipment.factory_number,
            inventory_number=equipment.inventory_number,
            verification_type=verification.verification_type if verification else "",
            verification_interval=verification.verification_interval if verification else 0,
            verification_date=verification.verification_date if verification else None,
            verification_due=verification.verification_due if verification else None,
            verification_plan=verification.verification_plan if verification else None,
            verification_state=verification.verification_state if verification else "",
            status=verification.status if verification else "",
            department=responsibility.department if responsibility else None,
            responsible_person=responsibility.responsible_person if responsibility else None,
            verifier_org=responsibility.verifier_org if responsibility else None
        )

    def delete_equipment_full(self, equipment_id: int) -> bool:
        """
        Удалить оборудование со всеми связанными данными
        """
        equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
        if not equipment:
            return False

        # Удаляем связанные данные
        self.db.query(Finance).filter(Finance.equipment_model_id == equipment_id).delete()
        self.db.query(Responsibility).filter(Responsibility.equipment_id == equipment_id).delete()
        self.db.query(Verification).filter(Verification.equipment_id == equipment_id).delete()

        # Удаляем оборудование
        self.db.delete(equipment)
        self.db.commit()

        return True

    def get_equipment_by_id(self, equipment_id: int) -> Optional[MainTableResponse]:
        """
        Получить оборудование по ID со всеми связанными данными
        """
        query = (
            select(
                Equipment.id.label("equipment_id"),
                Equipment.equipment_name,
                Equipment.equipment_model,
                Equipment.factory_number,
                Equipment.inventory_number,
                Verification.verification_type,
                Verification.verification_interval,
                Verification.verification_date,
                Verification.verification_due,
                Verification.verification_plan,
                Verification.verification_state,
                Verification.status,
                Responsibility.department,
                Responsibility.responsible_person,
                Responsibility.verifier_org
            )
            .select_from(Equipment)
            .join(Verification, Equipment.id == Verification.equipment_id, isouter=True)
            .join(Responsibility, Equipment.id == Responsibility.equipment_id, isouter=True)
            .where(Equipment.id == equipment_id)
        )

        result = self.db.execute(query).fetchone()

        if not result:
            return None

        return MainTableResponse(
            equipment_id=result.equipment_id,
            equipment_name=result.equipment_name,
            equipment_model=result.equipment_model,
            factory_number=result.factory_number,
            inventory_number=result.inventory_number,
            verification_type=result.verification_type or "",
            verification_interval=result.verification_interval or 0,
            verification_date=result.verification_date,
            verification_due=result.verification_due,
            verification_plan=result.verification_plan,
            verification_state=result.verification_state or "",
            status=result.status or "",
            department=result.department,
            responsible_person=result.responsible_person,
            verifier_org=result.verifier_org
        )