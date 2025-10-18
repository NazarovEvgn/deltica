# deltica/backend/routes/health.py

import logging
import os
import psutil
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.core.database import get_db
from backend.utils.auth import get_current_active_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Мониторинг"])


@router.get("/")
def health_check():
    """
    Базовая проверка работоспособности API.
    Доступна без аутентификации.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.get("/system")
def get_system_info(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Получить информацию о состоянии системы (только для администратора).

    Возвращает:
    - Статус подключения к БД
    - Информацию об использовании CPU и памяти
    - Информацию о дисковом пространстве
    - Количество файлов логов
    """
    # Проверка подключения к БД
    db_status = "ok"
    db_error = None
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "error"
        db_error = str(e)
        logger.error(
            f"Database health check failed: {str(e)}",
            extra={"event": "health_check_failed", "component": "database"}
        )

    # Информация о системе
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Информация о логах
    logs_dir = Path("backend/logs")
    log_files = list(logs_dir.glob("*.log*")) if logs_dir.exists() else []
    total_log_size = sum(f.stat().st_size for f in log_files)

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": {
            "status": db_status,
            "error": db_error
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2)
        },
        "logs": {
            "count": len(log_files),
            "total_size_mb": round(total_log_size / (1024**2), 2)
        }
    }


@router.get("/logs")
def get_logs(
    limit: int = 100,
    current_user = Depends(get_current_active_admin)
):
    """
    Получить последние записи из лога (только для администратора).

    Args:
        limit: Количество последних строк (по умолчанию 100, макс 1000)

    Returns:
        Список последних записей лога
    """
    # Ограничиваем лимит
    limit = min(limit, 1000)

    log_file = Path("backend/logs/deltica.log")

    if not log_file.exists():
        return {
            "logs": [],
            "message": "Файл логов не найден"
        }

    try:
        # Читаем последние N строк файла
        with open(log_file, 'r', encoding='utf-8') as f:
            # Читаем все строки и берём последние N
            all_lines = f.readlines()
            last_lines = all_lines[-limit:] if len(all_lines) > limit else all_lines

        return {
            "logs": [line.strip() for line in last_lines],
            "count": len(last_lines),
            "total_lines": len(all_lines)
        }
    except Exception as e:
        logger.error(
            f"Failed to read log file: {str(e)}",
            extra={"event": "log_read_failed", "error": str(e)}
        )
        return {
            "logs": [],
            "error": f"Ошибка чтения файла: {str(e)}"
        }
