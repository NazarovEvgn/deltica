# deltica/backend/app/models.py

from sqlalchemy import Column, Integer, Float, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_name = Column(String, nullable=False)
    equipment_model = Column(String, nullable=False)
    equipment_type = Column(Enum('SI', 'IO'), nullable=False)
    equipment_specs = Column(String)
    factory_number = Column(String, nullable=False)
    inventory_number = Column(String, nullable=False)
    equipment_year = Column(Integer, nullable=False)

    verifications = relationship("Verification", back_populates="equipment")


class Verification(Base):
    __tablename__ = "verification"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    verification_type = Column(Enum('calibration', 'verification', 'certification'), nullable=False)
    registry_number = Column(String)
    verification_interval = Column(Integer, nullable=False)
    verification_date = Column(Date, nullable=False)
    verification_due = Column(Date, nullable=False)
    verification_plan = Column(Date, nullable=False)
    verification_state = Column(Enum(
        'state_work',
        'state_storage',
        'state_verification',
        'state_repair',
        'state_archived'
    ), nullable=False)
    status = Column(Enum(
        'status_fit',
        'status_expired',
        'status_expiring',
        'status_storage',
        'status_verification',
        'status_repair'
    ), nullable=False)

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