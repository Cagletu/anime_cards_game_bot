import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в .env файле")

APP_DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"

# Определяем, запущено ли из alembic
is_alembic = False
if sys.argv and len(sys.argv) > 0:
    script_name = sys.argv[0].lower()
    is_alembic = "alembic" in script_name

if is_alembic:
    # Для alembic - синхронный engine
    sync_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    from sqlalchemy import create_engine
    engine = create_engine(sync_url, echo=APP_DEBUG)
else:
    # Для приложения - асинхронный
    engine = create_async_engine(DATABASE_URL, echo=APP_DEBUG, future=True)

# Базовый класс для моделей
Base = declarative_base()

if not is_alembic:
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async def get_db():
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
