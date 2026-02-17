from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. Create the Async Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False, # Set to True if you want to see SQL queries in console
    future=True
)

# 2. Create the Session Factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Base class for our models
Base = declarative_base()

# 4. Dependency Injection for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session