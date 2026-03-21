from fastapi import FastAPI
from app.api.v1 import endpoints
from app.db.database import engine, Base, AsyncSessionLocal
from app.db.models import User
from app.core.security import get_password_hash
from app.core.config import settings
from sqlalchemy import select
app = FastAPI(title="Tuwunel Monitor")
# Подключаем роуты
app.include_router(endpoints.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    # 1. Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Проверяем и создаем/обновляем админа
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == settings.ADMIN_USERNAME))
        user = result.scalar_one_or_none()

        # Хешируем пароль из .env
        hashed_pwd = get_password_hash(settings.ADMIN_PASSWORD)

        if not user:
            # Если пользователя нет - создаем
            print(f"Creating default admin user '{settings.ADMIN_USERNAME}'...")
            new_user = User(
                username=settings.ADMIN_USERNAME,
                hashed_password=hashed_pwd,
                role="admin"
            )
            session.add(new_user)
        else:
            # Если пользователь есть - обновляем пароль (чтобы совпадал с .env)
            # Это полезно, если вы хотите сменить пароль через конфиг
            if user.hashed_password != hashed_pwd:
                print(f"Updating password for admin user...")
                user.hashed_password = hashed_pwd

        await session.commit()

@app.get("/")
def read_root():
    return {"status": "Server Monitor is running"}

