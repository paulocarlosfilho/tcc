import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import User, Base
from app.auth import get_password_hash
from app.config import DATABASE_URL
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco de dados
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def seed_data():
    """
    Popula o banco de dados com dados iniciais essenciais para os testes.
    """
    async with engine.begin() as conn:
        # Cria as tabelas se não existirem
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Verificar e criar o usuário de teste (médico)
        test_user_username = "medico.teste"
        result = await db.execute(select(User).where(User.username == test_user_username))
        if not result.scalars().first():
            logger.info(f"Usuário '{test_user_username}' não encontrado. Criando...")
            hashed_password = get_password_hash("password123")
            test_user = User(
                username=test_user_username,
                email="medico.teste@example.com",
                hashed_password=hashed_password,
                role="doctor"
            )
            db.add(test_user)
            await db.commit()
            logger.info(f"Usuário '{test_user_username}' criado com sucesso.")
        else:
            logger.info(f"Usuário '{test_user_username}' já existe. Nenhuma ação necessária.")

async def main():
    logger.info("Iniciando o processo de seeding do banco de dados...")
    try:
        await seed_data()
        logger.info("Seeding concluído com sucesso.")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante o seeding: {e}", exc_info=True)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())