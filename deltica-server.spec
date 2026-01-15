# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os

block_cipher = None

# Функция для сбора файлов backend БЕЗ папки uploads
# ВАЖНО: uploads/ намеренно НЕ включена в сборку!
# Причина: runtime папка для файлов пользователей, должна быть пустой при установке
def get_backend_datas():
    datas = []
    # uploads НАМЕРЕННО отсутствует в списке - это runtime папка
    backend_subdirs = ['app', 'core', 'routes', 'services', 'middleware', 'utils', 'database_dumps']

    for subdir in backend_subdirs:
        src_path = os.path.join('backend', subdir)
        if os.path.exists(src_path):
            datas.append((src_path, os.path.join('backend', subdir)))

    return datas

a = Analysis(
    ['backend/core/main.py'],
    pathex=[],
    binaries=[],
    datas=get_backend_datas(),
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'passlib.handlers.bcrypt',
        'sqlalchemy.sql.default_comparator',
        'pydantic_settings',
        'dateutil',
        'dateutil.relativedelta',
        'jose',
        'jose.jwt',
        'jose.jws',
        'jose.jwk',
        'jose.exceptions',
        'pandas',
        'psycopg',
        'psycopg2',
        'alembic.operations',
        'docxtpl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy.tests',
        'scipy',
        'pytest',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='deltica-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
