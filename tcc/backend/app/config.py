import os

# URL do banco de dados, com um valor padrão para o ambiente Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/sus_db")