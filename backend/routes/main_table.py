# deltica/backend/routes/main_table.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.services.main_table import MainTableService
from backend.app.schemas import MainTableResponse, MainTableCreate, MainTableUpdate


router = APIRouter(prefix="/main-table", tags=["main-table"])


def get_db():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[MainTableResponse])
def get_all_equipment_data(db: Session = Depends(get_db)):
    """
    Получить все данные оборудования с верификацией и ответственностью
    """
    service = MainTableService(db)
    return service.get_all_data()


@router.get("/{equipment_id}", response_model=MainTableResponse)
def get_equipment_by_id(equipment_id: int, db: Session = Depends(get_db)):
    """
    Получить оборудование по ID со всеми связанными данными
    """
    service = MainTableService(db)
    equipment = service.get_equipment_by_id(equipment_id)

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Оборудование с ID {equipment_id} не найдено"
        )

    return equipment


@router.get("/{equipment_id}/full")
def get_equipment_full_by_id(equipment_id: int, db: Session = Depends(get_db)):
    """
    Получить полные данные оборудования по ID для редактирования
    """
    service = MainTableService(db)
    equipment = service.get_equipment_full_by_id(equipment_id)

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Оборудование с ID {equipment_id} не найдено"
        )

    return equipment


@router.post("/", response_model=MainTableResponse)
def create_equipment(equipment_data: MainTableCreate, db: Session = Depends(get_db)):
    """
    Создать новое оборудование со всеми связанными данными
    """
    service = MainTableService(db)

    try:
        return service.create_equipment_full(equipment_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании оборудования: {str(e)}"
        )


@router.put("/{equipment_id}", response_model=MainTableResponse)
def update_equipment(
    equipment_id: int,
    equipment_data: MainTableUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить оборудование со всеми связанными данными
    """
    service = MainTableService(db)

    updated_equipment = service.update_equipment_full(equipment_id, equipment_data)

    if not updated_equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Оборудование с ID {equipment_id} не найдено"
        )

    return updated_equipment


@router.delete("/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """
    Удалить оборудование со всеми связанными данными
    """
    service = MainTableService(db)

    if not service.delete_equipment_full(equipment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Оборудование с ID {equipment_id} не найдено"
        )

    return {"detail": f"Оборудование с ID {equipment_id} успешно удалено"}