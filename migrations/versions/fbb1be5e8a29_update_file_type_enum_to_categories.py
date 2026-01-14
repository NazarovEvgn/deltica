"""update_file_type_enum_to_categories

Revision ID: fbb1be5e8a29
Revises: 2bd9d6d79313
Create Date: 2026-01-14 19:43:13.937518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbb1be5e8a29'
down_revision: Union[str, Sequence[str], None] = '2bd9d6d79313'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Конвертируем enum в VARCHAR
    op.execute("ALTER TABLE equipment_files ALTER COLUMN file_type DROP DEFAULT")
    op.execute("ALTER TABLE archived_equipment_files ALTER COLUMN file_type DROP DEFAULT")
    op.execute("ALTER TABLE equipment_files ALTER COLUMN file_type TYPE VARCHAR")
    op.execute("ALTER TABLE archived_equipment_files ALTER COLUMN file_type TYPE VARCHAR")

    # 2. Обновляем существующие данные на новые категории (теперь это VARCHAR)
    # certificate/passport/other -> general_docs
    # technical_doc -> verification_docs
    op.execute("""
        UPDATE equipment_files
        SET file_type = 'general_docs'
        WHERE file_type IN ('certificate', 'passport', 'other')
    """)

    op.execute("""
        UPDATE equipment_files
        SET file_type = 'verification_docs'
        WHERE file_type = 'technical_doc'
    """)

    op.execute("""
        UPDATE archived_equipment_files
        SET file_type = 'general_docs'
        WHERE file_type IN ('certificate', 'passport', 'other')
    """)

    op.execute("""
        UPDATE archived_equipment_files
        SET file_type = 'verification_docs'
        WHERE file_type = 'technical_doc'
    """)

    # 3. Удаляем старый enum и создаем новый
    op.execute("DROP TYPE IF EXISTS file_type_enum CASCADE")
    op.execute("CREATE TYPE file_type_enum AS ENUM ('verification_docs', 'general_docs', 'active_certificate')")

    # 4. Возвращаем колонку к типу enum
    op.execute("ALTER TABLE equipment_files ALTER COLUMN file_type TYPE file_type_enum USING file_type::file_type_enum")
    op.execute("ALTER TABLE archived_equipment_files ALTER COLUMN file_type TYPE file_type_enum USING file_type::file_type_enum")
    op.execute("ALTER TABLE equipment_files ALTER COLUMN file_type SET DEFAULT 'general_docs'")
    op.execute("ALTER TABLE archived_equipment_files ALTER COLUMN file_type SET DEFAULT 'general_docs'")


def downgrade() -> None:
    """Downgrade schema."""
    # Обратная миграция
    op.execute("ALTER TABLE equipment_files ALTER COLUMN file_type DROP DEFAULT")
    op.execute("ALTER TABLE archived_equipment_files ALTER COLUMN file_type DROP DEFAULT")
    op.execute("ALTER TABLE equipment_files ALTER COLUMN file_type TYPE VARCHAR")
    op.execute("ALTER TABLE archived_equipment_files ALTER COLUMN file_type TYPE VARCHAR")

    # Пересоздаем старый enum
    op.execute("DROP TYPE IF EXISTS file_type_enum CASCADE")
    op.execute("CREATE TYPE file_type_enum AS ENUM ('certificate', 'passport', 'technical_doc', 'other')")

    # Возвращаем данные к старым категориям
    op.execute("UPDATE equipment_files SET file_type = 'other' WHERE file_type = 'general_docs'")
    op.execute("UPDATE equipment_files SET file_type = 'technical_doc' WHERE file_type = 'verification_docs'")
    op.execute("UPDATE equipment_files SET file_type = 'other' WHERE file_type = 'active_certificate'")
    op.execute("UPDATE archived_equipment_files SET file_type = 'other' WHERE file_type = 'general_docs'")
    op.execute("UPDATE archived_equipment_files SET file_type = 'technical_doc' WHERE file_type = 'verification_docs'")
    op.execute("UPDATE archived_equipment_files SET file_type = 'other' WHERE file_type = 'active_certificate'")

    # Возвращаем колонку к типу enum
    op.execute("ALTER TABLE equipment_files ALTER COLUMN file_type TYPE file_type_enum USING file_type::file_type_enum")
    op.execute("ALTER TABLE archived_equipment_files ALTER COLUMN file_type TYPE file_type_enum USING file_type::file_type_enum")
    op.execute("ALTER TABLE equipment_files ALTER COLUMN file_type SET DEFAULT 'other'")
    op.execute("ALTER TABLE archived_equipment_files ALTER COLUMN file_type SET DEFAULT 'other'")
