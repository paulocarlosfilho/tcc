import asyncio
import os
from app.database import engine, Base

async def reset_db():
    print("🧹 Limpando banco de dados para o teste final...")
    if os.path.exists("./blockchain_sus.db"):
        os.remove("./blockchain_sus.db")
        print("✅ Arquivo .db removido.")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tabelas recriadas com sucesso.")

if __name__ == "__main__":
    asyncio.run(reset_db())
