# deltica/backend/routes/archive.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.services.archive import ArchiveService
from backend.app.schemas import ArchiveResponse, ArchiveRequest, ArchiveFullResponse, ArchiveReasonUpdate


router = APIRouter(prefix="/archive", tags=["archive"])


def get_db():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/equipment/{equipment_id}", response_model=ArchiveResponse)
def archive_equipment(
    equipment_id: int,
    archive_request: Optional[ArchiveRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Архивировать оборудование (перенести в архивные таблицы и удалить из основных)
    """
    service = ArchiveService(db)

    archive_reason = None
    if archive_request:
        archive_reason = archive_request.archive_reason

    try:
        archived = service.archive_equipment(equipment_id, archive_reason)
        if not archived:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Оборудование с ID {equipment_id} не найдено"
            )
        return archived
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при архивировании оборудования: {str(e)}"
        )


@router.get("/", response_model=List[ArchiveResponse])
def get_archived_equipment(db: Session = Depends(get_db)):
    """
    Получить список всего архивного оборудования
    """
    service = ArchiveService(db)
    return service.get_all_archived()


@router.patch("/{archived_equipment_id}/reason", response_model=ArchiveResponse)
def update_archive_reason(
    archived_equipment_id: int,
    reason_update: ArchiveReasonUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить причину архивации для архивного оборудования.
    """
    service = ArchiveService(db)

    updated = service.update_archive_reason(archived_equipment_id, reason_update.archive_reason)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Архивное оборудование с ID {archived_equipment_id} не найдено"
        )

    return updated


@router.get("/{archived_equipment_id}", response_model=ArchiveResponse)
def get_archived_equipment_by_id(archived_equipment_id: int, db: Session = Depends(get_db)):
    """
    Получить детали архивного оборудования по ID
    """
    service = ArchiveService(db)
    archived = service.get_archived_by_id(archived_equipment_id)

    if not archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Архивное оборудование с ID {archived_equipment_id} не найдено"
        )

    return archived


@router.get("/{archived_equipment_id}/full", response_model=ArchiveFullResponse)
def get_archived_equipment_full(archived_equipment_id: int, db: Session = Depends(get_db)):
    """
    Получить полные данные архивного оборудования (включая верификацию, ответственность, финансы и файлы)
    """
    service = ArchiveService(db)
    archived_full = service.get_archived_full(archived_equipment_id)

    if not archived_full:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Архивное оборудование с ID {archived_equipment_id} не найдено"
        )

    return archived_full


@router.post("/restore/{archived_equipment_id}")
def restore_equipment(archived_equipment_id: int, db: Session = Depends(get_db)):
    """
    Восстановить оборудование из архива (вернуть в основные таблицы)
    """
    service = ArchiveService(db)

    try:
        restored = service.restore_equipment(archived_equipment_id)
        if not restored:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Архивное оборудование с ID {archived_equipment_id} не найдено"
            )
        return {
            "detail": f"Оборудование успешно восстановлено из архива",
            "equipment_id": restored.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при восстановлении оборудования: {str(e)}"
        )


@router.delete("/{archived_equipment_id}")
def delete_archived_equipment(archived_equipment_id: int, db: Session = Depends(get_db)):
    """
    Удалить оборудование из архива навсегда
    """
    service = ArchiveService(db)

    if not service.delete_archived(archived_equipment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Архивное оборудование с ID {archived_equipment_id} не найдено"
        )

    return {"detail": f"Архивное оборудование с ID {archived_equipment_id} удалено навсегда"}
