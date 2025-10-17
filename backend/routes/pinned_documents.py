# deltica/backend/routes/pinned_documents.py

import os
from pathlib import Path
from typing import List
from urllib.parse import quote
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.app.models import PinnedDocument, User
from backend.app.schemas import PinnedDocumentResponse
from backend.utils.auth import get_current_user, get_current_active_admin

router = APIRouter(prefix="/pinned-documents", tags=["pinned-documents"])

# Константы
UPLOAD_DIR = Path("backend/uploads/pinned_documents")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 МБ в байтах
ALLOWED_EXTENSIONS = {".pdf"}  # Только PDF файлы


def get_file_extension(filename: str) -> str:
    """Получить расширение файла."""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    """Проверить, разрешено ли расширение файла."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    """
    Санитизация имени файла для безопасности.
    Поддерживает кириллицу и пробелы для удобства пользователей.
    """
    # Удаляем опасные символы пути
    dangerous_chars = ['/', '\\', '..', ':']
    safe_filename = filename
    for char in dangerous_chars:
        safe_filename = safe_filename.replace(char, '_')
    return safe_filename


@router.get("/", response_model=List[PinnedDocumentResponse])
def get_pinned_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список всех закрепленных документов.
    Доступно для всех аутентифицированных пользователей.
    """
    documents = db.query(PinnedDocument).order_by(PinnedDocument.uploaded_at.desc()).all()
    return documents


@router.post("/upload", response_model=PinnedDocumentResponse)
async def upload_pinned_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Загрузить новый закрепленный документ (только PDF).
    Доступно только для администраторов.

    - **file**: Загружаемый PDF файл
    """
    # Проверка расширения файла (только PDF)
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый тип файла. Разрешены только PDF файлы."
        )

    # Чтение файла и проверка размера
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE / (1024*1024):.0f} МБ"
        )

    # Создание директории если не существует
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Санитизация имени файла
    safe_filename = sanitize_filename(file.filename)

    # Проверка на уникальность имени файла
    file_path = UPLOAD_DIR / safe_filename
    counter = 1
    original_stem = Path(safe_filename).stem
    original_ext = Path(safe_filename).suffix

    while file_path.exists():
        safe_filename = f"{original_stem}_{counter}{original_ext}"
        file_path = UPLOAD_DIR / safe_filename
        counter += 1

    # Сохранение файла на диск
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Сохранение информации о файле в БД
    relative_path = f"pinned_documents/{safe_filename}"

    db_document = PinnedDocument(
        file_name=file.filename,  # Оригинальное имя
        file_path=relative_path,
        file_size=file_size,
        uploaded_by=current_user.username
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


@router.get("/view/{document_id}")
def view_pinned_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Открыть документ для просмотра в браузере.
    Доступно для всех аутентифицированных пользователей.
    """
    db_document = db.query(PinnedDocument).filter(PinnedDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Документ не найден")

    file_path = Path("backend/uploads") / db_document.file_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден на диске")

    # Кодируем имя файла для корректной работы с кириллицей
    encoded_filename = quote(db_document.file_name)

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.get("/download/{document_id}")
def download_pinned_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Скачать документ (принудительное скачивание).
    Доступно для всех аутентифицированных пользователей.
    """
    db_document = db.query(PinnedDocument).filter(PinnedDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Документ не найден")

    file_path = Path("backend/uploads") / db_document.file_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден на диске")

    # Кодируем имя файла для корректной работы с кириллицей
    encoded_filename = quote(db_document.file_name)

    return FileResponse(
        path=str(file_path),
        filename=db_document.file_name,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.delete("/{document_id}")
def delete_pinned_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Удалить закрепленный документ.
    Доступно только для администраторов.
    """
    db_document = db.query(PinnedDocument).filter(PinnedDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Документ не найден")

    # Удаление файла с диска
    file_path = Path("backend/uploads") / db_document.file_path
    if file_path.exists():
        file_path.unlink()

    # Удаление записи из БД
    db.delete(db_document)
    db.commit()

    return {"message": "Документ успешно удален"}
