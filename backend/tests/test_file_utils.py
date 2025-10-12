# deltica/backend/tests/test_file_utils.py

import pytest
from backend.routes.files import (
    get_file_extension,
    is_allowed_file,
    sanitize_filename,
    get_media_type
)


class TestFileExtension:
    """Тесты для получения расширения файла."""

    def test_get_extension_pdf(self):
        assert get_file_extension("document.pdf") == ".pdf"

    def test_get_extension_uppercase(self):
        assert get_file_extension("DOCUMENT.PDF") == ".pdf"

    def test_get_extension_mixed_case(self):
        assert get_file_extension("Document.PdF") == ".pdf"

    def test_get_extension_with_path(self):
        assert get_file_extension("/path/to/file.docx") == ".docx"

    def test_get_extension_multiple_dots(self):
        assert get_file_extension("archive.tar.gz") == ".gz"

    def test_get_extension_no_extension(self):
        assert get_file_extension("README") == ""


class TestAllowedFiles:
    """Тесты для проверки допустимых расширений."""

    def test_allowed_pdf(self):
        assert is_allowed_file("document.pdf") == True

    def test_allowed_docx(self):
        assert is_allowed_file("report.docx") == True

    def test_allowed_jpg(self):
        assert is_allowed_file("photo.jpg") == True

    def test_allowed_jpeg(self):
        assert is_allowed_file("image.jpeg") == True

    def test_allowed_png(self):
        assert is_allowed_file("screenshot.png") == True

    def test_allowed_xls(self):
        assert is_allowed_file("spreadsheet.xls") == True

    def test_allowed_xlsx(self):
        assert is_allowed_file("data.xlsx") == True

    def test_allowed_doc(self):
        assert is_allowed_file("old_doc.doc") == True

    def test_disallowed_exe(self):
        assert is_allowed_file("virus.exe") == False

    def test_disallowed_sh(self):
        assert is_allowed_file("script.sh") == False

    def test_disallowed_py(self):
        assert is_allowed_file("code.py") == False

    def test_disallowed_no_extension(self):
        assert is_allowed_file("README") == False

    def test_allowed_uppercase(self):
        assert is_allowed_file("DOCUMENT.PDF") == True


class TestSanitizeFilename:
    """Тесты для санитизации имен файлов."""

    def test_sanitize_simple(self):
        result = sanitize_filename("document.pdf")
        assert result == "document.pdf"

    def test_sanitize_with_spaces(self):
        result = sanitize_filename("my document.pdf")
        assert result == "my_document.pdf"

    def test_sanitize_path_traversal(self):
        result = sanitize_filename("../../etc/passwd")
        # Точки и подчеркивания допустимы, слеши заменяются
        assert result == ".._.._etc_passwd"
        assert "/" not in result

    def test_sanitize_windows_path(self):
        result = sanitize_filename("..\\..\\windows\\system32\\config")
        assert "\\" not in result

    def test_sanitize_special_chars(self):
        result = sanitize_filename("file@#$%^&*().pdf")
        assert result == "file_________.pdf"

    def test_sanitize_cyrillic(self):
        # Кириллица должна быть заменена на underscore для безопасности
        result = sanitize_filename("Документ.pdf")
        assert result == "________.pdf"

    def test_sanitize_mixed(self):
        result = sanitize_filename("Test File (2023) - копия.pdf")
        # Кириллица заменяется на underscore, остальное остается
        assert result == "Test_File__2023__-______.pdf"

    def test_sanitize_only_safe_chars(self):
        result = sanitize_filename("test_file-2023.v1.pdf")
        assert result == "test_file-2023.v1.pdf"

    def test_sanitize_empty(self):
        result = sanitize_filename("")
        assert result == ""


class TestMediaType:
    """Тесты для определения MIME-типов."""

    def test_media_type_pdf(self):
        assert get_media_type("document.pdf") == "application/pdf"

    def test_media_type_doc(self):
        assert get_media_type("old.doc") == "application/msword"

    def test_media_type_docx(self):
        assert get_media_type("new.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def test_media_type_xls(self):
        assert get_media_type("old.xls") == "application/vnd.ms-excel"

    def test_media_type_xlsx(self):
        assert get_media_type("new.xlsx") == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def test_media_type_jpg(self):
        assert get_media_type("photo.jpg") == "image/jpeg"

    def test_media_type_jpeg(self):
        assert get_media_type("image.jpeg") == "image/jpeg"

    def test_media_type_png(self):
        assert get_media_type("screenshot.png") == "image/png"

    def test_media_type_unknown(self):
        assert get_media_type("unknown.xyz") == "application/octet-stream"

    def test_media_type_uppercase(self):
        assert get_media_type("DOCUMENT.PDF") == "application/pdf"

    def test_media_type_no_extension(self):
        assert get_media_type("README") == "application/octet-stream"
