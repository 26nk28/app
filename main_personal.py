# main_personal.py

import asyncio
import logging

# 1️⃣ Import your DB engine, Base & init from personal_agent.db
from personal_agent.db import engine, Base, init_db

# 2️⃣ Import your user-agent functions from personal_agent.agent
from personal_agent.agent import get_or_create_user, run_frontend

# 3️⃣ Import your backend updater
import personal_agent.backend_service as backend_service

# Hide SQLAlchemy INFO/DEBUG logs
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def reset_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await init_db()
    print("✅ Database schema reset.")


async def main():
    # 1) Reset / migrate your schema
    await reset_schema()

    # 2) Create or fetch your "Test User"
    user_id, agent_id = await get_or_create_user(
        name="Test User",
        email="test@example.com",
        phone="+0000000000"
    )
    print(f"🆔 user_id={user_id}, agent_id={agent_id}\n")

    # 3) Start your async backend updater
    backend_task = asyncio.create_task(
        backend_service.run_backend(user_id, agent_id)
    )
    print("🔄 Backend persona-updater started.")

    # 4) Run frontend REPL and backend updater in parallel
    await asyncio.gather(
        run_frontend(user_id, agent_id),
        backend_task
    )


if __name__ == "__main__":
    asyncio.run(main())
