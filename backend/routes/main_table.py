# deltica/backend/routes/main_table.py

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.services.main_table import MainTableService
from backend.app.schemas import MainTableResponse, MainTableCreate, MainTableUpdate
from backend.utils.auth import get_current_user

logger = logging.getLogger(__name__)


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
def create_equipment(
    equipment_data: MainTableCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Создать новое оборудование со всеми связанными данными
    """
    service = MainTableService(db)

    try:
        result = service.create_equipment_full(equipment_data)
        logger.info(
            f"Equipment created: {equipment_data.equipment_name}",
            extra={
                "event": "equipment_created",
                "user": current_user.username,
                "equipment_id": result.equipment_id,
                "equipment_name": equipment_data.equipment_name,
                "equipment_type": equipment_data.equipment_type
            }
        )
        return result
    except Exception as e:
        logger.error(
            f"Failed to create equipment: {str(e)}",
            extra={
                "event": "equipment_create_failed",
                "user": current_user.username,
                "equipment_name": equipment_data.equipment_name,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании оборудования: {str(e)}"
        )


@router.put("/{equipment_id}", response_model=MainTableResponse)
def update_equipment(
    equipment_id: int,
    equipment_data: MainTableUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Обновить оборудование со всеми связанными данными
    """
    service = MainTableService(db)

    updated_equipment = service.update_equipment_full(equipment_id, equipment_data)

    if not updated_equipment:
        logger.warning(
            f"Equipment update failed - not found: ID {equipment_id}",
            extra={
                "event": "equipment_update_failed",
                "user": current_user.username,
                "equipment_id": equipment_id,
                "reason": "not_found"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Оборудование с ID {equipment_id} не найдено"
        )

    logger.info(
        f"Equipment updated: ID {equipment_id}",
        extra={
            "event": "equipment_updated",
            "user": current_user.username,
            "equipment_id": equipment_id
        }
    )

    return updated_equipment


@router.delete("/{equipment_id}")
def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Удалить оборудование со всеми связанными данными
    """
    service = MainTableService(db)

    if not service.delete_equipment_full(equipment_id):
        logger.warning(
            f"Equipment deletion failed - not found: ID {equipment_id}",
            extra={
                "event": "equipment_delete_failed",
                "user": current_user.username,
                "equipment_id": equipment_id,
                "reason": "not_found"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Оборудование с ID {equipment_id} не найдено"
        )

    logger.info(
        f"Equipment deleted: ID {equipment_id}",
        extra={
            "event": "equipment_deleted",
            "user": current_user.username,
            "equipment_id": equipment_id
        }
    )

    return {"detail": f"Оборудование с ID {equipment_id} успешно удалено"}