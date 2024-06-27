
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import POSTGRES_USER, POSTGRES_PASSWORD,POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=True)
TaskSessionLocal = sessionmaker(
    expire_on_commit=False,
    bind=engine, 
    class_=AsyncSession
)

# Separate session for tracking
TrackSessionLocal = sessionmaker(
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession
)

Base = declarative_base()

async def get_task_db():
    async with TaskSessionLocal() as session:
        yield session

async def get_track_db():
    async with TrackSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)




