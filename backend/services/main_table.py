# deltica/backend/services/main_table.py

from typing import List, Optional
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from backend.app.models import Equipment, Verification, Responsibility, Finance
from backend.app.schemas import MainTableResponse, MainTableCreate, MainTableUpdate


def calculate_status(verification_due: date, verification_state: str) -> str:
    """
    Вычисляет status на основе verification_due и verification_state.

    Логика приоритетов:
    1. Если verification_state = 'state_verification', 'state_repair', 'state_storage', 'state_archived'
       → статус ВСЕГДА дублирует состояние (независимо от срока)
    2. Если verification_state = 'state_work':
       - Если CURRENT_DATE > verification_due → status_expired
       - Если verification_due - CURRENT_DATE <= 14 дней → status_expiring
       - Иначе → status_fit

    Args:
        verification_due: Дата окончания действия верификации (вычислена в БД)
        verification_state: Состояние оборудования

    Returns:
        Вычисленный status
    """
    # Маппинг состояний в статусы
    state_to_status_map = {
        "state_storage": "status_storage",
        "state_verification": "status_verification",
        "state_repair": "status_repair",
        "state_archived": "status_fit"
    }

    # Если состояние не 'state_work', то статус всегда дублирует состояние
    if verification_state in state_to_status_map:
        return state_to_status_map[verification_state]

    # Для 'state_work' проверяем срок верификации
    today = date.today()

    if today > verification_due:
        return "status_expired"

    days_until_due = (verification_due - today).days
    if days_until_due <= 14:
        return "status_expiring"

    return "status_fit"


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
                Equipment.equipment_type,
                Equipment.factory_number,
                Equipment.inventory_number,
                Equipment.equipment_year,
                Verification.verification_type,
                Verification.registry_number,
                Verification.verification_interval,
                Verification.verification_date,
                Verification.verification_due,
                Verification.verification_plan,
                Verification.verification_state,
                Verification.status,
                Responsibility.department,
                Responsibility.responsible_person,
                Responsibility.verifier_org,
                Finance.budget_item,
                Finance.code_rate,
                Finance.cost_rate,
                Finance.quantity,
                Finance.coefficient,
                Finance.total_cost,
                Finance.invoice_number,
                Finance.paid_amount,
                Finance.payment_date
            )
            .select_from(Equipment)
            .join(Verification, Equipment.id == Verification.equipment_id, isouter=True)
            .join(Responsibility, Equipment.id == Responsibility.equipment_id, isouter=True)
            .join(Finance, Equipment.id == Finance.equipment_model_id, isouter=True)
        )

        result = self.db.execute(query).fetchall()

        # Преобразование результата в список схем
        return [
            MainTableResponse(
                equipment_id=row.equipment_id,
                equipment_name=row.equipment_name,
                equipment_model=row.equipment_model,
                equipment_type=row.equipment_type,
                factory_number=row.factory_number,
                inventory_number=row.inventory_number,
                equipment_year=row.equipment_year,
                verification_type=row.verification_type or "",
                registry_number=row.registry_number,
                verification_interval=row.verification_interval or 0,
                verification_date=row.verification_date,
                verification_due=row.verification_due,
                verification_plan=row.verification_plan,
                verification_state=row.verification_state or "",
                status=row.status or "",
                department=row.department,
                responsible_person=row.responsible_person,
                verifier_org=row.verifier_org,
                budget_item=row.budget_item,
                code_rate=row.code_rate,
                cost_rate=row.cost_rate,
                quantity=row.quantity,
                coefficient=row.coefficient,
                total_cost=row.total_cost,
                invoice_number=row.invoice_number,
                paid_amount=row.paid_amount,
                payment_date=row.payment_date
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

        # Создаем верификацию (status временно устанавливаем в status_fit)
        verification = Verification(
            equipment_id=equipment.id,
            verification_type=data.verification_type,
            registry_number=data.registry_number,
            verification_interval=data.verification_interval,
            verification_date=data.verification_date,
            verification_plan=data.verification_plan,
            verification_state=data.verification_state,
            status="status_fit"  # Временное значение
        )

        self.db.add(verification)
        self.db.flush()  # БД вычислит verification_due как generated column
        self.db.refresh(verification)  # Получаем вычисленный verification_due

        # Теперь вычисляем правильный status на основе verification_due из БД
        calculated_status = calculate_status(
            verification_due=verification.verification_due,
            verification_state=verification.verification_state  # Используем значение из объекта
        )
        verification.status = calculated_status

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
            budget_item=data.budget_item,
            code_rate=data.code_rate,
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
            equipment_type=equipment.equipment_type,
            factory_number=equipment.factory_number,
            inventory_number=equipment.inventory_number,
            equipment_year=equipment.equipment_year,
            verification_type=verification.verification_type,
            registry_number=verification.registry_number,
            verification_interval=verification.verification_interval,
            verification_date=verification.verification_date,
            verification_due=verification.verification_due,
            verification_plan=verification.verification_plan,
            verification_state=verification.verification_state,
            status=verification.status,
            department=responsibility.department,
            responsible_person=responsibility.responsible_person,
            verifier_org=responsibility.verifier_org,
            budget_item=finance.budget_item,
            code_rate=finance.code_rate,
            cost_rate=finance.cost_rate,
            quantity=finance.quantity,
            coefficient=finance.coefficient,
            total_cost=finance.total_cost,
            invoice_number=finance.invoice_number,
            paid_amount=finance.paid_amount,
            payment_date=finance.payment_date
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
            verification.verification_plan = data.verification_plan
            verification.verification_state = data.verification_state

            # Флашим изменения, чтобы БД пересчитала verification_due
            self.db.flush()
            self.db.refresh(verification)

            # Теперь вычисляем правильный status на основе verification_due из БД
            calculated_status = calculate_status(
                verification_due=verification.verification_due,
                verification_state=verification.verification_state  # Используем обновленное значение
            )
            verification.status = calculated_status

        # Обновляем ответственность
        responsibility = self.db.query(Responsibility).filter(Responsibility.equipment_id == equipment_id).first()
        if responsibility:
            responsibility.department = data.department
            responsibility.responsible_person = data.responsible_person
            responsibility.verifier_org = data.verifier_org

        # Обновляем финансы
        finance = self.db.query(Finance).filter(Finance.equipment_model_id == equipment_id).first()
        if finance:
            finance.budget_item = data.budget_item
            finance.code_rate = data.code_rate
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
            equipment_type=equipment.equipment_type,
            factory_number=equipment.factory_number,
            inventory_number=equipment.inventory_number,
            equipment_year=equipment.equipment_year,
            verification_type=verification.verification_type if verification else "",
            registry_number=verification.registry_number if verification else None,
            verification_interval=verification.verification_interval if verification else 0,
            verification_date=verification.verification_date if verification else None,
            verification_due=verification.verification_due if verification else None,
            verification_plan=verification.verification_plan if verification else None,
            verification_state=verification.verification_state if verification else "",
            status=verification.status if verification else "",
            department=responsibility.department if responsibility else None,
            responsible_person=responsibility.responsible_person if responsibility else None,
            verifier_org=responsibility.verifier_org if responsibility else None,
            budget_item=finance.budget_item if finance else None,
            code_rate=finance.code_rate if finance else None,
            cost_rate=finance.cost_rate if finance else None,
            quantity=finance.quantity if finance else None,
            coefficient=finance.coefficient if finance else None,
            total_cost=finance.total_cost if finance else None,
            invoice_number=finance.invoice_number if finance else None,
            paid_amount=finance.paid_amount if finance else None,
            payment_date=finance.payment_date if finance else None
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
                Equipment.equipment_type,
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
            equipment_type=result.equipment_type,
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

    def get_equipment_full_by_id(self, equipment_id: int) -> Optional[dict]:
        """
        Получить полные данные оборудования по ID для редактирования
        """
        equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
        if not equipment:
            return None

        verification = self.db.query(Verification).filter(Verification.equipment_id == equipment_id).first()
        responsibility = self.db.query(Responsibility).filter(Responsibility.equipment_id == equipment_id).first()
        finance = self.db.query(Finance).filter(Finance.equipment_model_id == equipment_id).first()

        return {
            # Equipment fields
            "equipment_name": equipment.equipment_name,
            "equipment_model": equipment.equipment_model,
            "equipment_type": equipment.equipment_type,
            "equipment_specs": equipment.equipment_specs,
            "factory_number": equipment.factory_number,
            "inventory_number": equipment.inventory_number,
            "equipment_year": equipment.equipment_year,

            # Verification fields
            "verification_type": verification.verification_type if verification else "",
            "registry_number": verification.registry_number if verification else "",
            "verification_interval": verification.verification_interval if verification else 12,
            "verification_date": verification.verification_date if verification else None,
            "verification_due": verification.verification_due if verification else None,
            "verification_plan": verification.verification_plan if verification else None,
            "verification_state": verification.verification_state if verification else "",
            "status": verification.status if verification else "",

            # Responsibility fields
            "department": responsibility.department if responsibility else "",
            "responsible_person": responsibility.responsible_person if responsibility else "",
            "verifier_org": responsibility.verifier_org if responsibility else "",

            # Finance fields
            "budget_item": finance.budget_item if finance else "",
            "code_rate": finance.code_rate if finance else "",
            "cost_rate": finance.cost_rate if finance else None,
            "quantity": finance.quantity if finance else 1,
            "coefficient": finance.coefficient if finance else 1.0,
            "total_cost": finance.total_cost if finance else None,
            "invoice_number": finance.invoice_number if finance else "",
            "paid_amount": finance.paid_amount if finance else None,
            "payment_date": finance.payment_date if finance else None
        }