#deltica/backend/core/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.main_table import router as main_table_router
from backend.routes.files import router as files_router

app = FastAPI(title="Deltica API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_root():
    return {"message": "GET works"}

@app.post("/")
def post_root():
    return {"message": "POST works"}

app.include_router(main_table_router)
app.include_router(files_router)