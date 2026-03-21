from fastapi import APIRouter, Depends, HTTPException
from app.schemas.metrics import DashboardResponse
from app.services.monitor import MonitorService
from app.core.security import verify_token, create_access_token

# !!! ВОТ ЭТА СТРОКА ОБЯЗАТЕЛЬНА !!!
router = APIRouter()
# ----------------------------------

monitor_service = MonitorService()

# Эндпоинт для логина (получения токена)
@router.post("/token")
def login(username: str, password: str):
    # В реальном приложении здесь проверка по базе данных!
    if username == "admin" and password == "secret":
        token = create_access_token(data={"sub": username, "role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Дашборд
@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(user = Depends(verify_token)):
    return DashboardResponse(
        cpu=monitor_service.get_cpu_info(),
        ram=monitor_service.get_ram_info(),
        disks=monitor_service.get_disks_info()
    )

# Процессы
@router.get("/processes")
def get_processes(user = Depends(verify_token)):
    return monitor_service.get_processes()

# Убить процесс
@router.post("/process/{pid}/kill")
def kill_process(pid: int, user = Depends(verify_token)):
    if monitor_service.kill_process(pid):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Process not found")