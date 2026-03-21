from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import User
from app.schemas.metrics import DashboardResponse
from app.services.monitor import MonitorService
from app.core.security import verify_token, create_access_token, verify_password# !!! ВОТ ЭТА СТРОКА ОБЯЗАТЕЛЬНА !!!
router = APIRouter()
monitor_service = MonitorService()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
# Эндпоинт для логина (получения токена)
@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # 1. Ищем пользователя
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    # 2. Проверяем, существует ли пользователь
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # 3. ПРОВЕРКА ПАРОЛЯ (Этого не хватало!)
    # Сравниваем введенный пароль с хешем из базы
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # 4. Создаем токен (Исправлена переменная username на user.username)
    token = create_access_token(data={"sub": user.username, "role": user.role})

    return {"access_token": token, "token_type": "bearer"}

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