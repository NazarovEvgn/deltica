# deltica/backend/routes/documents.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from pydantic import BaseModel
from typing import List

from backend.core.database import get_db
from backend.services.documents import DocumentService
from backend.utils.auth import get_current_user
from backend.app.models import User


class GenerateLabelsRequest(BaseModel):
    """Схема запроса для пакетной генерации этикеток"""
    equipment_ids: List[int]

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/label/{equipment_id}")
def generate_label(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Генерировать и скачать этикетку для оборудования
    Доступно для всех аутентифицированных пользователей
    """
    service = DocumentService(db)

    try:
        file_path = service.generate_label(equipment_id)

        if not file_path:
            raise HTTPException(
                status_code=404,
                detail="Оборудование не найдено"
            )

        # Проверить, что файл существует
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=500,
                detail="Ошибка при генерации документа"
            )

        # Вернуть файл для скачивания
        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"Этикетка_{equipment_id}.docx",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''%D0%AD%D1%82%D0%B8%D0%BA%D0%B5%D1%82%D0%BA%D0%B0_{equipment_id}.docx"
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Шаблон не найден: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при генерации документа: {str(e)}"
        )


@router.post("/labels")
def generate_labels_batch(
    request: GenerateLabelsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Генерировать и скачать пакет этикеток для нескольких единиц оборудования
    Доступно для всех аутентифицированных пользователей
    """
    service = DocumentService(db)

    if not request.equipment_ids:
        raise HTTPException(
            status_code=400,
            detail="Список ID оборудования не может быть пустым"
        )

    try:
        file_path = service.generate_labels_batch(request.equipment_ids)

        if not file_path:
            raise HTTPException(
                status_code=404,
                detail="Не найдено оборудование для генерации этикеток"
            )

        # Проверить, что файл существует
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=500,
                detail="Ошибка при генерации документа"
            )

        # Вернуть файл для скачивания
        count = len(request.equipment_ids)
        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"Этикетки_{count}_шт.docx",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''%D0%AD%D1%82%D0%B8%D0%BA%D0%B5%D1%82%D0%BA%D0%B8_{count}_%D1%88%D1%82.docx"
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Шаблон не найден: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при генерации документа: {str(e)}"
        )

@router.post("/conservation-act")
def generate_conservation_act(
    request: GenerateLabelsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Генерировать акт консервации для нескольких единиц оборудования
    Доступно для всех аутентифицированных пользователей
    """
    service = DocumentService(db)

    if not request.equipment_ids:
        raise HTTPException(
            status_code=400,
            detail="Список ID оборудования не может быть пустым"
        )

    try:
        file_path = service.generate_conservation_act(request.equipment_ids)

        if not file_path:
            raise HTTPException(
                status_code=404,
                detail="Не найдено оборудование для генерации акта"
            )

        # Проверить, что файл существует
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=500,
                detail="Ошибка при генерации документа"
            )

        # Вернуть файл для скачивания
        count = len(request.equipment_ids)
        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"Акт_консервации_{count}_шт.docx",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''%D0%90%D0%BA%D1%82_%D0%BA%D0%BE%D0%BD%D1%81%D0%B5%D1%80%D0%B2%D0%B0%D1%86%D0%B8%D0%B8_{count}_%D1%88%D1%82.docx"
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Шаблон не найден: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при генерации акта консервации: {str(e)}"
        )


@router.get("/commissioning-template")
def download_commissioning_template(
    current_user: User = Depends(get_current_user)
):
    """
    Скачать шаблон акта ввода в эксплуатацию
    Доступно для всех аутентифицированных пользователей
    """
    template_path = Path("docs/docx-templates/template_new_entries.docx")
    
    if not template_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Шаблон не найден"
        )
    
    # Вернуть шаблон для скачивания
    return FileResponse(
        path=str(template_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="Акт_ввода_в_эксплуатацию.docx",
        headers={
            "Content-Disposition": "attachment; filename*=UTF-8''%D0%90%D0%BA%D1%82_%D0%B2%D0%B2%D0%BE%D0%B4%D0%B0_%D0%B2_%D1%8D%D0%BA%D1%81%D0%BF%D0%BB%D1%83%D0%B0%D1%82%D0%B0%D1%86%D0%B8%D1%8E.docx"
        }
    )
