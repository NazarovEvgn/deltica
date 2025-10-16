# deltica/backend/app/schemas.py

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class EquipmentTypeEnum(str, Enum):
    SI = "SI"
    IO = "IO"


class EquipmentBase(BaseModel):
    equipment_name: str
    equipment_model: str
    equipment_type: EquipmentTypeEnum
    equipment_specs: Optional[str] = None
    factory_number: str
    inventory_number: str
    equipment_year: int


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(EquipmentBase):
    class Config:
        from_attributes = True


class Equipment(EquipmentBase):
    id: int

    class Config:
        from_attributes = True


class VerificationBase(BaseModel):
    equipment_id: int
    verification_type: str
    registry_number: Optional[str]
    verification_interval: int
    verification_date: date
    verification_due: date
    verification_plan: date
    verification_state: str
    status: str

    @field_validator('verification_interval')
    @classmethod
    def validate_interval_multiple_of_12(cls, v: int) -> int:
        if v % 12 != 0:
            raise ValueError('Интервал верификации должен быть кратен 12 месяцам (12, 24, 36, 48 и т.д.)')
        if v < 12:
            raise ValueError('Интервал верификации должен быть не менее 12 месяцев')
        return v


class VerificationCreate(VerificationBase):
    pass


class VerificationUpdate(VerificationBase):
    class Config:
        from_attributes = True


class Verification(VerificationBase):
    id: int
    equipment: Equipment

    class Config:
        from_attributes = True


class ResponsibilityBase(BaseModel):
    equipment_id: int
    department: str
    responsible_person: str
    verifier_org: str


class ResponsibilityCreate(ResponsibilityBase):
    pass


class ResponsibilityUpdate(ResponsibilityBase):
    class Config:
        from_attributes = True


class Responsibility(ResponsibilityBase):
    id: int

    class Config:
        from_attributes = True


class FinanceBase(BaseModel):
    equipment_model_id: int
    cost_rate: Optional[float]
    quantity: int
    coefficient: float = Field(default=1.0)
    total_cost: Optional[float]
    invoice_number: Optional[str]
    paid_amount: Optional[float]
    payment_date: Optional[date]


class FinanceCreate(FinanceBase):
    pass


class FinanceUpdate(FinanceBase):
    class Config:
        from_attributes = True


class Finance(FinanceBase):
    id: int

    class Config:
        from_attributes = True


# Схемы для main_table
class MainTableResponse(BaseModel):
    equipment_id: int
    equipment_name: str
    equipment_model: str
    equipment_type: EquipmentTypeEnum
    factory_number: str
    inventory_number: str
    verification_type: str
    verification_interval: int
    verification_date: date
    verification_due: date
    verification_plan: date
    verification_state: str
    status: str
    department: Optional[str] = None
    responsible_person: Optional[str] = None
    verifier_org: Optional[str] = None

    class Config:
        from_attributes = True


class MainTableCreate(BaseModel):
    # Equipment fields
    equipment_name: str
    equipment_model: str
    equipment_type: EquipmentTypeEnum
    equipment_specs: Optional[str] = None
    factory_number: str
    inventory_number: str
    equipment_year: int

    # Verification fields
    verification_type: str
    registry_number: Optional[str] = None
    verification_interval: int
    verification_date: date
    verification_due: date
    verification_plan: date
    verification_state: str
    status: str

    # Responsibility fields
    department: str
    responsible_person: str
    verifier_org: str

    # Finance fields
    cost_rate: Optional[float] = None
    quantity: int
    coefficient: float = Field(default=1.0)
    total_cost: Optional[float] = None
    invoice_number: Optional[str] = None
    paid_amount: Optional[float] = None
    payment_date: Optional[date] = None


class MainTableUpdate(MainTableCreate):
    pass


# Схемы для EquipmentFile
class FileTypeEnum(str, Enum):
    certificate = "certificate"  # Свидетельство о поверке
    passport = "passport"  # Паспорт
    technical_doc = "technical_doc"  # Техническая документация
    other = "other"  # Прочее


class EquipmentFileBase(BaseModel):
    file_name: str
    file_type: FileTypeEnum = FileTypeEnum.other


class EquipmentFileResponse(EquipmentFileBase):
    id: int
    equipment_id: int
    file_path: str
    file_size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Схемы для архива
class ArchiveRequest(BaseModel):
    """Запрос на архивирование с опциональной причиной"""
    archive_reason: Optional[str] = None


class ArchiveResponse(BaseModel):
    """Ответ с данными архивного оборудования"""
    id: int
    original_id: int
    equipment_name: str
    equipment_model: str
    equipment_type: EquipmentTypeEnum
    equipment_specs: Optional[str] = None
    factory_number: str
    inventory_number: str
    equipment_year: int
    archived_at: datetime
    archive_reason: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== СХЕМЫ ДЛЯ АУТЕНТИФИКАЦИИ ====================

class UserRoleEnum(str, Enum):
    admin = "admin"
    laborant = "laborant"


class UserBase(BaseModel):
    username: str
    full_name: str
    department: str
    role: UserRoleEnum = UserRoleEnum.laborant


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str