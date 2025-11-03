# deltica/backend/routes/backup.py

import logging
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from backend.app.schemas import BackupHistoryResponse, BackupCreateResponse
from backend.services.backup import BackupService
from backend.utils.auth import get_current_active_admin

logger = logging.getLogger(__name__)

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
        logger.info(
            f"Backup created successfully: {backup.file_name}",
            extra={
                "event": "backup_created",
                "user": current_user.username,
                "backup_id": backup.id,
                "file_name": backup.file_name,
                "file_size": backup.file_size
            }
        )
        return BackupCreateResponse(
            message="Резервная копия успешно создана",
            backup=BackupHistoryResponse.model_validate(backup)
        )
    except Exception as e:
        logger.error(
            f"Backup creation failed: {str(e)}",
            extra={
                "event": "backup_failed",
                "user": current_user.username,
                "error": str(e)
            }
        )
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
        logger.warning(
            f"Backup deletion failed - not found: ID {backup_id}",
            extra={
                "event": "backup_delete_failed",
                "user": current_user.username,
                "backup_id": backup_id,
                "reason": "not_found"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Резервная копия с ID {backup_id} не найдена"
        )

    logger.info(
        f"Backup deleted: ID {backup_id}",
        extra={
            "event": "backup_deleted",
            "user": current_user.username,
            "backup_id": backup_id
        }
    )

    return None


@router.get("/export-excel")
def export_to_excel(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Экспортировать данные БД в Excel файл (только для администратора).
    Возвращает файл для скачивания.
    """
    service = BackupService()

    try:
        # Создаем Excel файл
        file_path = service.export_to_excel(db)

        # Кодируем имя файла для корректной работы с кириллицей
        encoded_filename = quote(file_path.name)

        logger.info(
            f"Excel export created: {file_path.name}",
            extra={
                "event": "excel_export_created",
                "user": current_user.username,
                "file_name": file_path.name
            }
        )

        # Возвращаем файл для скачивания
        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        logger.error(
            f"Excel export failed: {str(e)}",
            extra={
                "event": "excel_export_failed",
                "user": current_user.username,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка экспорта данных: {str(e)}"
        )
