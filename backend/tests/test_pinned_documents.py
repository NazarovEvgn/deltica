# deltica/backend/tests/test_pinned_documents.py

"""
Unit-тесты для API закрепленных документов.

Принципы:
- Полная изоляция: моки используются для аутентификации, нет зависимости от реальных паролей
- Независимость: каждый тест создает свое окружение (БД, файловая система)
- Тестируется только функционал pinned documents API, а не аутентификация
"""

import pytest
from io import BytesIO
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.core.main import app
from backend.core.database import get_db
from backend.app.models import User, PinnedDocument
from backend.utils.auth import get_current_user, get_current_active_admin


# ==================== ФИКСТУРЫ ====================

@pytest.fixture(scope="function")
def pinned_db_session():
    """Создать изолированную тестовую БД (SQLite in-memory)."""
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with engine.connect() as conn:
        # Таблица pinned_documents
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pinned_documents (
                id INTEGER PRIMARY KEY,
                file_name VARCHAR NOT NULL,
                file_path VARCHAR NOT NULL,
                file_size INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                uploaded_by VARCHAR NOT NULL
            )
        """))
        conn.commit()

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS pinned_documents"))
            conn.commit()


@pytest.fixture(scope="function")
def pinned_client(pinned_db_session):
    """Создать FastAPI TestClient с изолированной тестовой БД."""
    def override_get_db():
        try:
            yield pinned_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_pinned_upload_dir(monkeypatch):
    """Создать временную директорию для загрузки pinned documents."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Переопределяем UPLOAD_DIR в модуле pinned_documents
    from backend.routes import pinned_documents
    monkeypatch.setattr(pinned_documents, "UPLOAD_DIR", temp_path)

    yield temp_path

    # Очистка после теста
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_admin_user():
    """Создать мок-объект админа (без БД, без паролей)."""
    user = Mock(spec=User)
    user.id = 1
    user.username = "test_admin"
    user.full_name = "Test Admin"
    user.department = "Test Department"
    user.role = "admin"
    user.is_active = True
    return user


@pytest.fixture
def mock_laborant_user():
    """Создать мок-объект лаборанта (без БД, без паролей)."""
    user = Mock(spec=User)
    user.id = 2
    user.username = "test_laborant"
    user.full_name = "Test Laborant"
    user.department = "Test Lab"
    user.role = "laborant"
    user.is_active = True
    return user


@pytest.fixture
def client_as_admin(pinned_db_session, mock_admin_user):
    """Клиент с мокнутой аутентификацией как админ (отдельная БД сессия)."""
    def override_get_db():
        try:
            yield pinned_db_session
        finally:
            pass

    def override_get_current_user():
        return mock_admin_user

    def override_get_current_active_admin():
        return mock_admin_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_admin] = override_get_current_active_admin

    with TestClient(app) as test_client:
        yield test_client

    # Очистка
    app.dependency_overrides.clear()


@pytest.fixture
def client_as_laborant(pinned_db_session, mock_laborant_user):
    """Клиент с мокнутой аутентификацией как лаборант (отдельная БД сессия)."""
    def override_get_db():
        try:
            yield pinned_db_session
        finally:
            pass

    def override_get_current_user():
        return mock_laborant_user

    def override_get_current_active_admin():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Недостаточно прав доступа")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_admin] = override_get_current_active_admin

    with TestClient(app) as test_client:
        yield test_client

    # Очистка
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf_content():
    """Простой валидный PDF контент."""
    return b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"


# ==================== ТЕСТЫ ====================

class TestPinnedDocumentsAuth:
    """Тесты аутентификации и авторизации."""

    def test_get_documents_without_auth(self, pinned_client):
        """Получение документов без аутентификации должно возвращать 401."""
        response = pinned_client.get("/pinned-documents/")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_upload_without_auth(self, pinned_client, sample_pdf_content):
        """Загрузка документа без аутентификации должна возвращать 401."""
        response = pinned_client.post(
            "/pinned-documents/upload",
            files={"file": ("test.pdf", BytesIO(sample_pdf_content), "application/pdf")}
        )
        assert response.status_code == 401

    def test_upload_as_laborant(self, client_as_laborant, sample_pdf_content):
        """Загрузка документа как лаборант должна быть запрещена (403)."""
        response = client_as_laborant.post(
            "/pinned-documents/upload",
            files={"file": ("test.pdf", BytesIO(sample_pdf_content), "application/pdf")}
        )
        assert response.status_code == 403
        assert "недостаточно прав" in response.json()["detail"].lower()

    def test_delete_as_laborant(self, client_as_laborant):
        """Удаление документа как лаборант должно быть запрещено (403)."""
        response = client_as_laborant.delete("/pinned-documents/1")
        assert response.status_code == 403


class TestPinnedDocumentsUpload:
    """Тесты загрузки закрепленных документов."""

    def test_upload_pdf_success(self, client_as_admin, temp_pinned_upload_dir, sample_pdf_content):
        """Успешная загрузка PDF документа админом."""
        filename = "График поверки 2025.pdf"

        response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": (filename, BytesIO(sample_pdf_content), "application/pdf")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == filename
        assert data["file_size"] == len(sample_pdf_content)
        assert data["uploaded_by"] == "test_admin"
        assert "id" in data
        assert "uploaded_at" in data
        assert "pinned_documents/" in data["file_path"]

        # Проверяем, что файл создан на диске
        file_path = temp_pinned_upload_dir / filename
        assert file_path.exists()
        assert file_path.read_bytes() == sample_pdf_content

    def test_upload_cyrillic_filename(self, client_as_admin, temp_pinned_upload_dir, sample_pdf_content):
        """Загрузка файла с кириллическим именем."""
        filename = "Инструкция по метрологии.pdf"

        response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": (filename, BytesIO(sample_pdf_content), "application/pdf")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == filename

        # Файл должен быть создан с правильным именем
        file_path = temp_pinned_upload_dir / filename
        assert file_path.exists()

    def test_upload_duplicate_filename(self, client_as_admin, temp_pinned_upload_dir, sample_pdf_content):
        """Загрузка файла с дублирующимся именем (должен добавиться суффикс)."""
        filename = "график.pdf"

        # Первая загрузка
        response1 = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": (filename, BytesIO(sample_pdf_content), "application/pdf")}
        )
        assert response1.status_code == 200
        file_path_1 = response1.json()["file_path"]

        # Вторая загрузка с тем же именем
        response2 = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": (filename, BytesIO(sample_pdf_content), "application/pdf")}
        )
        assert response2.status_code == 200
        file_path_2 = response2.json()["file_path"]

        # Пути должны быть разные (второй файл должен получить суффикс)
        assert file_path_1 != file_path_2
        assert "_1" in file_path_2

    def test_upload_non_pdf_file(self, client_as_admin):
        """Загрузка не-PDF файла должна быть отклонена."""
        response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": ("document.docx", BytesIO(b"fake docx content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )

        assert response.status_code == 400
        assert "недопустимый тип файла" in response.json()["detail"].lower()
        assert "pdf" in response.json()["detail"].lower()

    def test_upload_file_too_large(self, client_as_admin):
        """Загрузка файла больше 50 МБ должна быть отклонена."""
        # 51 МБ контент
        large_content = b"x" * (51 * 1024 * 1024)

        response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": ("large.pdf", BytesIO(large_content), "application/pdf")}
        )

        assert response.status_code == 400
        assert "слишком большой" in response.json()["detail"].lower()
        assert "50" in response.json()["detail"]


class TestPinnedDocumentsList:
    """Тесты получения списка документов."""

    def test_get_empty_list(self, client_as_admin):
        """Получение пустого списка документов."""
        response = client_as_admin.get("/pinned-documents/")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_documents_list_as_admin(self, client_as_admin, sample_pdf_content):
        """Получение списка документов админом."""
        # Загружаем два документа
        client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": ("doc1.pdf", BytesIO(sample_pdf_content), "application/pdf")}
        )
        client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": ("doc2.pdf", BytesIO(sample_pdf_content), "application/pdf")}
        )

        # Получаем список
        response = client_as_admin.get("/pinned-documents/")

        assert response.status_code == 200
        documents = response.json()
        assert len(documents) == 2
        assert any(doc["file_name"] == "doc1.pdf" for doc in documents)
        assert any(doc["file_name"] == "doc2.pdf" for doc in documents)

        # Проверяем поля в каждом документе
        for doc in documents:
            assert "id" in doc
            assert "file_name" in doc
            assert "file_size" in doc
            assert "uploaded_at" in doc
            assert "uploaded_by" in doc
            assert doc["uploaded_by"] == "test_admin"

    def test_get_documents_list_as_laborant(self, client_as_laborant, pinned_db_session, sample_pdf_content):
        """Получение списка документов лаборантом (должны видеть все документы)."""
        # Создаем документ напрямую в БД (имитация загрузки админом)
        from backend.app.models import PinnedDocument
        doc = PinnedDocument(
            file_name="instruction.pdf",
            file_path="pinned_documents/instruction.pdf",
            file_size=len(sample_pdf_content),
            uploaded_by="test_admin"
        )
        pinned_db_session.add(doc)
        pinned_db_session.commit()

        # Лаборант получает список
        response = client_as_laborant.get("/pinned-documents/")

        assert response.status_code == 200
        documents = response.json()
        assert len(documents) == 1
        assert documents[0]["file_name"] == "instruction.pdf"


class TestPinnedDocumentsView:
    """Тесты просмотра документов."""

    def test_view_document_success(self, client_as_admin, sample_pdf_content):
        """Успешный просмотр документа."""
        # Загружаем документ
        upload_response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": ("view_test.pdf", BytesIO(sample_pdf_content), "application/pdf")}
        )
        doc_id = upload_response.json()["id"]

        # Просматриваем документ
        view_response = client_as_admin.get(f"/pinned-documents/view/{doc_id}")

        assert view_response.status_code == 200
        assert view_response.content == sample_pdf_content
        assert "inline" in view_response.headers["content-disposition"].lower()
        assert "application/pdf" in view_response.headers["content-type"]

    def test_view_document_as_laborant(self, client_as_laborant, pinned_db_session):
        """Просмотр документа лаборантом (проверка доступа, не 403)."""
        # Создаем запись в БД (имитация загрузки админом)
        from backend.app.models import PinnedDocument
        doc = PinnedDocument(
            file_name="shared.pdf",
            file_path="pinned_documents/shared.pdf",
            file_size=100,
            uploaded_by="test_admin"
        )
        pinned_db_session.add(doc)
        pinned_db_session.commit()
        pinned_db_session.refresh(doc)

        # Лаборант просматривает документ (файла нет на диске, будет 404, НО НЕ 403)
        view_response = client_as_laborant.get(f"/pinned-documents/view/{doc.id}")

        # Лаборант имеет ДОСТУП к просмотру (не 403 Forbidden)
        # Файла нет на диске, поэтому ожидаем 404, а не 403
        assert view_response.status_code == 404  # File not found, но доступ есть
        assert "не найден" in view_response.json()["detail"].lower()

    def test_view_document_not_found(self, client_as_admin):
        """Просмотр несуществующего документа."""
        response = client_as_admin.get("/pinned-documents/view/99999")

        assert response.status_code == 404
        assert "не найден" in response.json()["detail"].lower()

    def test_view_without_auth(self, pinned_client):
        """Просмотр документа без аутентификации."""
        response = pinned_client.get("/pinned-documents/view/1")
        assert response.status_code == 401


class TestPinnedDocumentsDownload:
    """Тесты скачивания документов."""

    def test_download_document_success(self, client_as_admin, sample_pdf_content):
        """Успешное скачивание документа."""
        filename = "download_test.pdf"

        # Загружаем документ
        upload_response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": (filename, BytesIO(sample_pdf_content), "application/pdf")}
        )
        doc_id = upload_response.json()["id"]

        # Скачиваем документ
        download_response = client_as_admin.get(f"/pinned-documents/download/{doc_id}")

        assert download_response.status_code == 200
        assert download_response.content == sample_pdf_content
        assert "attachment" in download_response.headers["content-disposition"].lower()
        assert filename in download_response.headers["content-disposition"]

    def test_download_cyrillic_filename(self, client_as_admin, sample_pdf_content):
        """Скачивание файла с кириллическим именем (RFC 5987)."""
        filename = "Инструкция по МО.pdf"

        # Загружаем документ
        upload_response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": (filename, BytesIO(sample_pdf_content), "application/pdf")}
        )
        doc_id = upload_response.json()["id"]

        # Скачиваем документ
        download_response = client_as_admin.get(f"/pinned-documents/download/{doc_id}")

        assert download_response.status_code == 200
        # Проверяем, что есть RFC 5987 encoded filename
        assert "filename*=UTF-8''" in download_response.headers["content-disposition"]

    def test_download_as_laborant(self, client_as_laborant, pinned_db_session):
        """Скачивание документа лаборантом (проверка доступа, не 403)."""
        # Создаем запись в БД (имитация загрузки админом)
        from backend.app.models import PinnedDocument
        doc = PinnedDocument(
            file_name="public.pdf",
            file_path="pinned_documents/public.pdf",
            file_size=100,
            uploaded_by="test_admin"
        )
        pinned_db_session.add(doc)
        pinned_db_session.commit()
        pinned_db_session.refresh(doc)

        # Лаборант скачивает документ (файла нет на диске, будет 404, НО НЕ 403)
        download_response = client_as_laborant.get(f"/pinned-documents/download/{doc.id}")

        # Лаборант имеет ДОСТУП к скачиванию (не 403 Forbidden)
        # Файла нет на диске, поэтому ожидаем 404, а не 403
        assert download_response.status_code == 404  # File not found, но доступ есть
        assert "не найден" in download_response.json()["detail"].lower()

    def test_download_document_not_found(self, client_as_admin):
        """Скачивание несуществующего документа."""
        response = client_as_admin.get("/pinned-documents/download/99999")

        assert response.status_code == 404


class TestPinnedDocumentsDelete:
    """Тесты удаления документов."""

    def test_delete_document_success(self, client_as_admin, sample_pdf_content):
        """Успешное удаление документа."""
        filename = "delete_test.pdf"

        # Загружаем документ
        upload_response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": (filename, BytesIO(sample_pdf_content), "application/pdf")}
        )
        doc_id = upload_response.json()["id"]

        # Удаляем документ
        delete_response = client_as_admin.delete(f"/pinned-documents/{doc_id}")

        assert delete_response.status_code == 200
        assert "успешно удален" in delete_response.json()["message"].lower()

        # Проверяем, что документ удален из БД
        list_response = client_as_admin.get("/pinned-documents/")
        documents = list_response.json()
        assert not any(doc["id"] == doc_id for doc in documents)

    def test_delete_document_not_found(self, client_as_admin):
        """Удаление несуществующего документа."""
        response = client_as_admin.delete("/pinned-documents/99999")

        assert response.status_code == 404

    def test_delete_document_file_missing(self, client_as_admin, temp_pinned_upload_dir, sample_pdf_content):
        """Удаление документа, когда файл уже удален с диска (graceful handling)."""
        # Загружаем документ
        upload_response = client_as_admin.post(
            "/pinned-documents/upload",
            files={"file": ("missing.pdf", BytesIO(sample_pdf_content), "application/pdf")}
        )
        doc_id = upload_response.json()["id"]
        file_path = temp_pinned_upload_dir / "missing.pdf"

        # Вручную удаляем файл с диска
        if file_path.exists():
            file_path.unlink()

        # Удаляем документ из БД (должно пройти успешно даже если файла нет)
        delete_response = client_as_admin.delete(f"/pinned-documents/{doc_id}")

        assert delete_response.status_code == 200
