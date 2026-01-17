# deltica/backend/app/models.py

from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Enum, ForeignKey, Computed, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_name = Column(String, nullable=False)
    equipment_model = Column(String, nullable=False)
    equipment_type = Column(Enum('SI', 'IO', name='equipment_type_enum'), nullable=False)
    equipment_specs = Column(String)
    factory_number = Column(String, nullable=False)
    inventory_number = Column(String, nullable=False)
    equipment_year = Column(Integer, nullable=False)

    verifications = relationship("Verification", back_populates="equipment")
    files = relationship("EquipmentFile", back_populates="equipment", cascade="all, delete-orphan")


class Verification(Base):
    __tablename__ = "verification"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    verification_type = Column(Enum('calibration', 'verification', 'certification', name='verification_type_enum'), nullable=False)
    registry_number = Column(String)
    verification_interval = Column(Integer, nullable=False)
    verification_date = Column(Date, nullable=False)
    verification_due = Column(Date, Computed("(verification_date + make_interval(months => verification_interval) - interval '1 day')::date"))
    verification_plan = Column(Date, nullable=False)
    verification_state = Column(Enum(
        'state_work',
        'state_storage',
        'state_verification',
        'state_repair',
        'state_archived',
        name='verification_state_enum'
    ), nullable=False)
    status = Column(Enum(
        'status_fit',
        'status_expired',
        'status_expiring',
        'status_storage',
        'status_verification',
        'status_repair',
        name='verification_status_enum'
    ), nullable=False)  # Auto-calculated by trigger

    equipment = relationship("Equipment", back_populates="verifications")


class Responsibility(Base):
    __tablename__ = "responsibility"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    department = Column(String, nullable=False)
    responsible_person = Column(String, nullable=False)
    verifier_org = Column(String, nullable=False)


class Finance(Base):
    __tablename__ = "finance"

    id = Column(Integer, primary_key=True, index=True)
    equipment_model_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    budget_item = Column(String, nullable=False)  # Статья бюджета (обязательное поле)
    code_rate = Column(String)  # Тариф (опциональное поле)
    cost_rate = Column(Float)
    quantity = Column(Integer, nullable=False)
    coefficient = Column(Float, default=1.0)
    total_cost = Column(Float)
    invoice_number = Column(String)
    paid_amount = Column(Float)
    payment_date = Column(Date)


class EquipmentFile(Base):
    __tablename__ = "equipment_files"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)  # Оригинальное имя файла
    file_path = Column(String, nullable=False)  # Относительный путь к файлу
    file_type = Column(Enum('verification_docs', 'general_docs', 'active_certificate', name='file_type_enum'), nullable=False, default='general_docs')
    file_size = Column(Integer, nullable=False)  # Размер в байтах
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active_certificate = Column(Boolean, default=False)  # Флаг действующего сертификата
    sort_order = Column(Integer, default=0)  # Порядок сортировки для drag & drop

    equipment = relationship("Equipment", back_populates="files")


# ==================== АРХИВНЫЕ ТАБЛИЦЫ ====================

class ArchivedEquipment(Base):
    """Архивная таблица для списанного оборудования"""
    __tablename__ = "archived_equipment"

    id = Column(Integer, primary_key=True, index=True)
    original_id = Column(Integer, nullable=False, index=True)  # ID оригинальной записи
    equipment_name = Column(String, nullable=False)
    equipment_model = Column(String, nullable=False)
    equipment_type = Column(Enum('SI', 'IO', name='equipment_type_enum'), nullable=False)
    equipment_specs = Column(String)
    factory_number = Column(String, nullable=False)
    inventory_number = Column(String, nullable=False)
    equipment_year = Column(Integer, nullable=False)

    # Метаданные архивирования
    archived_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    archive_reason = Column(String)  # Причина списания (опционально)

    # Relationships
    archived_verifications = relationship("ArchivedVerification", back_populates="archived_equipment", cascade="all, delete-orphan")
    archived_files = relationship("ArchivedEquipmentFile", back_populates="archived_equipment", cascade="all, delete-orphan")


class ArchivedVerification(Base):
    """Архивная таблица для данных поверки"""
    __tablename__ = "archived_verification"

    id = Column(Integer, primary_key=True, index=True)
    archived_equipment_id = Column(Integer, ForeignKey("archived_equipment.id", ondelete="CASCADE"), nullable=False)
    original_equipment_id = Column(Integer, nullable=False)  # ID оригинального equipment
    verification_type = Column(Enum('calibration', 'verification', 'certification', name='verification_type_enum'), nullable=False)
    registry_number = Column(String)
    verification_interval = Column(Integer, nullable=False)
    verification_date = Column(Date, nullable=False)
    verification_due = Column(Date, nullable=False)  # Копируем computed значение
    verification_plan = Column(Date, nullable=False)
    verification_state = Column(Enum(
        'state_work',
        'state_storage',
        'state_verification',
        'state_repair',
        'state_archived',
        name='verification_state_enum'
    ), nullable=False)
    status = Column(Enum(
        'status_fit',
        'status_expired',
        'status_expiring',
        'status_storage',
        'status_verification',
        'status_repair',
        name='verification_status_enum'
    ), nullable=False)

    archived_equipment = relationship("ArchivedEquipment", back_populates="archived_verifications")


class ArchivedResponsibility(Base):
    """Архивная таблица для данных об ответственных"""
    __tablename__ = "archived_responsibility"

    id = Column(Integer, primary_key=True, index=True)
    archived_equipment_id = Column(Integer, ForeignKey("archived_equipment.id", ondelete="CASCADE"), nullable=False)
    original_equipment_id = Column(Integer, nullable=False)
    department = Column(String, nullable=False)
    responsible_person = Column(String, nullable=False)
    verifier_org = Column(String, nullable=False)


class ArchivedFinance(Base):
    """Архивная таблица для финансовых данных"""
    __tablename__ = "archived_finance"

    id = Column(Integer, primary_key=True, index=True)
    archived_equipment_id = Column(Integer, ForeignKey("archived_equipment.id", ondelete="CASCADE"), nullable=False)
    original_equipment_id = Column(Integer, nullable=False)
    budget_item = Column(String, nullable=False)  # Статья бюджета (обязательное поле)
    code_rate = Column(String)  # Тариф (опциональное поле)
    cost_rate = Column(Float)
    quantity = Column(Integer, nullable=False)
    coefficient = Column(Float, default=1.0)
    total_cost = Column(Float)
    invoice_number = Column(String)
    paid_amount = Column(Float)
    payment_date = Column(Date)


class ArchivedEquipmentFile(Base):
    """Архивная таблица для файлов"""
    __tablename__ = "archived_equipment_files"

    id = Column(Integer, primary_key=True, index=True)
    archived_equipment_id = Column(Integer, ForeignKey("archived_equipment.id", ondelete="CASCADE"), nullable=False)
    original_equipment_id = Column(Integer, nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(Enum('verification_docs', 'general_docs', 'active_certificate', name='file_type_enum'), nullable=False, default='general_docs')
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False)  # Копируем дату оригинальной загрузки
    sort_order = Column(Integer, default=0)  # Порядок сортировки

    archived_equipment = relationship("ArchivedEquipment", back_populates="archived_files")


# ==================== ПОЛЬЗОВАТЕЛИ И АУТЕНТИФИКАЦИЯ ====================

class User(Base):
    """Модель пользователя для аутентификации и авторизации"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)  # Логин для входа
    password_hash = Column(String, nullable=True)  # Хеш пароля (bcrypt) - nullable для Windows auth
    windows_username = Column(String, unique=True, nullable=True, index=True)  # Windows имя пользователя для SSO
    full_name = Column(String, nullable=False)  # ФИО (из responsible_person)
    department = Column(String, nullable=False)  # Подразделение
    role = Column(Enum('admin', 'laborant', name='user_role_enum'), nullable=False, default='laborant')
    is_active = Column(Boolean, default=True, nullable=False)  # Активен ли пользователь
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ==================== ЗАКРЕПЛЕННЫЕ ДОКУМЕНТЫ ====================

class PinnedDocument(Base):
    """Модель для хранения закрепленных PDF документов (инструкции, графики, регламенты и т.п.)"""
    __tablename__ = "pinned_documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)  # Оригинальное имя файла
    file_path = Column(String, nullable=False)  # Относительный путь к файлу
    file_size = Column(Integer, nullable=False)  # Размер в байтах
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by = Column(String, nullable=False)  # Username пользователя, загрузившего файл


# ==================== РЕЗЕРВНОЕ КОПИРОВАНИЕ ====================

class BackupHistory(Base):
    """Модель для хранения истории резервных копий БД"""
    __tablename__ = "backup_history"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)  # Имя файла backup'а
    file_path = Column(String, nullable=False)  # Полный путь к файлу
    file_size = Column(Integer, nullable=False)  # Размер в байтах
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String, nullable=False)  # Username администратора
    status = Column(Enum('success', 'failed', name='backup_status_enum'), nullable=False, default='success')
    error_message = Column(String)  # Сообщение об ошибке, если backup failed


# ==================== БАЛАНС ПО ДОГОВОРАМ ====================

class Contract(Base):
    """Модель для записной книжки админа - баланс по договорам с исполнителями"""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    executor_name = Column(String, nullable=False)  # Название исполнителя
    contract_number = Column(String, nullable=False)  # Номер договора
    valid_until = Column(Date, nullable=False)  # Действует до
    contract_amount = Column(Float, nullable=False)  # Сумма по договору
    spent_amount = Column(Float, default=0.0, nullable=False)  # Израсходовано
    balance = Column(Float, Computed("contract_amount - spent_amount"))  # Остаток (автоматический расчет)
    current_balance = Column(Float)  # Текущий баланс (ручной ввод)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())