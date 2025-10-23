# app/init_db.py
import asyncio
from app.database import engine
from app.models import Base

async def init_models():
    async with engine.begin() as conn:
        print("Creating tables in Neon...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_models())
