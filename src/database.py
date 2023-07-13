from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession,
)

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME


DATABASE_URL = f'postgresql+asyncpg:' \
               f'//{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine,
                                         class_=AsyncSession,
                                         expire_on_commit=False,
                                         )

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронное получение сессии."""
    async with async_session_maker() as session:
        yield session
