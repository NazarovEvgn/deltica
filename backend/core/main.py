#deltica/backend/core/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.main_table import router as main_table_router
from backend.routes.files import router as files_router
from backend.routes.archive import router as archive_router
from backend.routes.auth import router as auth_router
from backend.routes.pinned_documents import router as pinned_documents_router
from backend.routes.backup import router as backup_router
from backend.routes.health import router as health_router
from backend.routes.contracts import router as contracts_router
from backend.routes.documents import router as documents_router
from backend.core.logging_config import setup_logging
from backend.middleware.logging_middleware import LoggingMiddleware

# Инициализация системы логирования
setup_logging()

app = FastAPI(title="Deltica API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend URL (default)
        "http://localhost:5174"   # Frontend URL (alternative port)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования HTTP запросов
app.add_middleware(LoggingMiddleware)

@app.get("/")
def get_root():
    return {"message": "GET works"}

@app.post("/")
def post_root():
    return {"message": "POST works"}

app.include_router(auth_router)
app.include_router(main_table_router)
app.include_router(files_router)
app.include_router(archive_router)
app.include_router(pinned_documents_router)
app.include_router(backup_router)
app.include_router(health_router)
app.include_router(contracts_router)
app.include_router(documents_router)