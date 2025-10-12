# deltica/backend/app/models.py

from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Enum, ForeignKey, Computed
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
    file_type = Column(Enum('certificate', 'passport', 'technical_doc', 'other', name='file_type_enum'), nullable=False, default='other')
    file_size = Column(Integer, nullable=False)  # Размер в байтах
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    equipment = relationship("Equipment", back_populates="files")