import asyncio

from app.db.models import Base
from app.deps import engine


async def criar_tabelas()->None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Tabelas criadas!")


if __name__ == "__main__":
    asyncio.run(criar_tabelas())