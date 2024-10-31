from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

# Настройки базы данных
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
