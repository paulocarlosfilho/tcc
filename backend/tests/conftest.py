import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base, get_db
from app.main import app

# Usa a mesma URL do banco de dados de teste do workflow de CI
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://testuser:testpassword@localhost:5432/testdb")

# Cria um novo engine de banco de dados para os testes
engine = create_async_engine(TEST_DATABASE_URL)

# Cria um novo sessionmaker para os testes
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Cria as tabelas antes da sessão de testes e as remove depois.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fornece uma nova sessão de banco de dados para cada função de teste.
    """
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Cria um novo AsyncClient para cada função de teste, com a dependência
    do banco de dados substituída para usar a sessão de teste isolada.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    
    # Limpa a substituição da dependência após o teste
    del app.dependency_overrides[get_db]