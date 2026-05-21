import asyncio
import os
import sys
from typing import AsyncGenerator

# Adiciona o diretório raiz do projeto (backend) ao sys.path
# para resolver problemas de importação em diferentes ambientes de execução.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base, get_db
from app.main import app as fastapi_app

# Usa a mesma URL do banco de dados de teste do workflow de CI, mas aponta para a porta 5433
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://testuser:testpassword@localhost:5433/testdb")


@pytest.fixture(scope="function")
async def db_engine():
    """
    Cria um engine de banco de dados isolado para cada teste.
    'yields' o engine e garante que ele seja descartado no final, fechando todas as conexões.
    """
    engine = create_async_engine(TEST_DATABASE_URL)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def setup_database(db_engine):
    """
    Cria as tabelas antes de cada teste e as remove depois, usando o engine do teste.
    """
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_engine, monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    """
    Cria um cliente de teste com uma transação de banco de dados totalmente isolada
    usando o engine específico do teste.
    
    Usa monkeypatch para garantir que o ciclo de vida (lifespan) da aplicação também
    use o engine de teste, prevenindo vazamento de conexões.
    """
    # Substitui o engine global da aplicação pelo engine de teste.
    # O monkeypatch garante que a alteração seja desfeita após o teste.
    import app.database
    monkeypatch.setattr(app.database, "engine", db_engine)

    # Cria um sessionmaker para o engine específico deste teste
    TestingSessionLocal = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    # Inicia uma conexão com o banco de dados de teste
    connection = await db_engine.connect()
    # Inicia uma transação principal
    transaction = await connection.begin()

    # Cria uma sessão de teste, vinculando-a à conexão existente
    session = TestingSessionLocal(bind=connection)

    # Inicia um "savepoint" para permitir transações aninhadas na aplicação
    await connection.begin_nested()

    # Substitui a dependência `get_db` para usar a sessão de teste
    fastapi_app.dependency_overrides[get_db] = lambda: session

    try:
        async with AsyncClient(app=fastapi_app, base_url="http://test") as c:
            yield c
    finally:
        # Limpeza
        del fastapi_app.dependency_overrides[get_db]
        await session.close()
        await transaction.rollback()
        await connection.close()