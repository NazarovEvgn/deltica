from fastapi import FastAPI
from backend.routes.main_table import router as main_table_router

app = FastAPI(title="Deltica API", version="1.0.0")

@app.get("/")
def get_root():
    return {"message": "GET works"}

@app.post("/")
def post_root():
    return {"message": "POST works"}

app.include_router(main_table_router)