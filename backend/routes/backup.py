# deltica/backend/routes/backup.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from backend.app.schemas import BackupHistoryResponse, BackupCreateResponse
from backend.services.backup import BackupService
from backend.utils.auth import get_current_active_admin

router = APIRouter(prefix="/backup", tags=["Резервное копирование"])


@router.post("/create", response_model=BackupCreateResponse, status_code=status.HTTP_201_CREATED)
def create_backup(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Создать резервную копию БД (только для администратора).
    """
    service = BackupService()

    try:
        # Создаем backup
        backup = service.create_backup(db, current_user.username)
        return BackupCreateResponse(
            message="Резервная копия успешно создана",
            backup=BackupHistoryResponse.model_validate(backup)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/history", response_model=List[BackupHistoryResponse])
def get_backup_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Получить историю резервных копий (только для администратора).
    По умолчанию возвращает последние 20 записей.
    """
    service = BackupService()
    backups = service.get_backup_history(db, limit)
    return [BackupHistoryResponse.model_validate(b) for b in backups]


@router.get("/check", response_model=dict)
def check_backup_availability(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Проверить, можно ли создать новый backup (только для администратора).
    Возвращает информацию о возможности создания backup.
    """
    service = BackupService()
    can_create, error_msg = service.can_create_backup(db)

    return {
        "can_create": can_create,
        "message": error_msg if not can_create else "Можно создать резервную копию"
    }


@router.delete("/{backup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_backup(
    backup_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Удалить резервную копию по ID (только для администратора).
    Удаляет как файл, так и запись из истории.
    """
    service = BackupService()

    if not service.delete_backup(db, backup_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резервная копия с ID {backup_id} не найдена"
        )

    return None
