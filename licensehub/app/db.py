from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

engine: AsyncEngine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)

AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session