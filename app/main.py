from fastapi import FastAPI
from app.api.v1 import endpoints

app = FastAPI(title="Tuwunel Monitor")

# Подключаем роуты
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "Server Monitor is running"}