# deltica/backend/routes/contracts.py

"""
API эндпоинты для работы с балансом по договорам (записная книжка админа)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db
from backend.app.models import Contract
from backend.app.schemas import ContractCreate, ContractUpdate, ContractResponse
from backend.utils.auth import get_current_active_admin

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"],
    dependencies=[Depends(get_current_active_admin)]  # Только для администраторов
)


@router.get("/", response_model=List[ContractResponse])
def get_all_contracts(db: Session = Depends(get_db)):
    """Получить список всех договоров"""
    contracts = db.query(Contract).order_by(Contract.valid_until.desc()).all()
    return contracts


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    """Получить договор по ID"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Договор не найден")
    return contract


@router.post("/", response_model=ContractResponse)
def create_contract(contract: ContractCreate, db: Session = Depends(get_db)):
    """Создать новый договор"""
    db_contract = Contract(**contract.model_dump())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@router.put("/{contract_id}", response_model=ContractResponse)
def update_contract(
    contract_id: int,
    contract: ContractUpdate,
    db: Session = Depends(get_db)
):
    """Обновить договор"""
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="Договор не найден")

    # Обновляем поля
    for key, value in contract.model_dump().items():
        setattr(db_contract, key, value)

    db.commit()
    db.refresh(db_contract)
    return db_contract


@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    """Удалить договор"""
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="Договор не найден")

    db.delete(db_contract)
    db.commit()
    return {"message": "Договор успешно удален"}
