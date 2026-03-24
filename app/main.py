from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import endpoints
from app.db.database import engine, Base, AsyncSessionLocal
from app.db.models import User
from app.core.security import get_password_hash, generate_random_password
from sqlalchemy import select



@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Логика Запуска (Startup) ---

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    DEFAULT_ADMIN_USERNAME = "admin"

    # Проверяем и создаем админа
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()

        if not user:
            password = generate_random_password()
            print(f"Creating default admin user '{DEFAULT_ADMIN_USERNAME}'...")

            new_user = User(
                username=DEFAULT_ADMIN_USERNAME,
                hashed_password=get_password_hash(password),
                role="admin"
            )
            session.add(new_user)

            print("\n" + "=" * 40)
            print(f" Login:    {DEFAULT_ADMIN_USERNAME}")
            print(f" Password: {password}")
            print("=" * 40 + "\n")

        await session.commit()

    yield

app = FastAPI(title="Tuwunel Monitor", lifespan=lifespan)

# Подключаем роуты
app.include_router(endpoints.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"status": "Server Monitor is running"}