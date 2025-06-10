from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from utils.config import (
    PERSONAL_DATABASE_URL, 
    GROUP_DATABASE_URL,
    USER_ONBOARDING_DATABASE_URL,
    GROUP_ONBOARDING_DATABASE_URL
)

# ═══════════════════ PERSONAL AGENT DATABASE ═══════════════════
personal_engine: AsyncEngine = create_async_engine(
    PERSONAL_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

PersonalAsyncSessionLocal = sessionmaker(
    bind=personal_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

PersonalBase = declarative_base()

# ═══════════════════ GROUP DATABASE ═══════════════════
group_engine: AsyncEngine = create_async_engine(
    GROUP_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

GroupAsyncSessionLocal = sessionmaker(
    bind=group_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

GroupBase = declarative_base()

# ═══════════════════ USER ONBOARDING DATABASE ═══════════════════
user_onboarding_engine: AsyncEngine = create_async_engine(
    USER_ONBOARDING_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

UserOnboardingAsyncSessionLocal = sessionmaker(
    bind=user_onboarding_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

UserOnboardingBase = declarative_base()

# ═══════════════════ GROUP ONBOARDING DATABASE ═══════════════════
group_onboarding_engine: AsyncEngine = create_async_engine(
    GROUP_ONBOARDING_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

GroupOnboardingAsyncSessionLocal = sessionmaker(
    bind=group_onboarding_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

GroupOnboardingBase = declarative_base()

# ═══════════════════ DATABASE INITIALIZATION ═══════════════════
async def init_personal_db():
    """Create all tables in personal database."""
    async with personal_engine.begin() as conn:
        await conn.run_sync(PersonalBase.metadata.create_all)
    print("✅ Personal agent database initialized")

async def init_group_db():
    """Create all tables in group database."""
    async with group_engine.begin() as conn:
        await conn.run_sync(GroupBase.metadata.create_all)
    print("✅ Group database initialized")

async def init_user_onboarding_db():
    """Create all tables in user onboarding database."""
    async with user_onboarding_engine.begin() as conn:
        await conn.run_sync(UserOnboardingBase.metadata.create_all)
    print("✅ User onboarding database initialized")

async def init_group_onboarding_db():
    """Create all tables in group onboarding database."""
    async with group_onboarding_engine.begin() as conn:
        await conn.run_sync(GroupOnboardingBase.metadata.create_all)
    print("✅ Group onboarding database initialized")

async def init_all_databases():
    """Initialize all databases."""
    await init_personal_db()
    await init_group_db()
    await init_user_onboarding_db()
    await init_group_onboarding_db()
    print("✅ All databases initialized")

async def reset_personal_schema():
    """Reset personal database schema."""
    async with personal_engine.begin() as conn:
        await conn.run_sync(PersonalBase.metadata.drop_all)
    await init_personal_db()
    print("✅ Personal database schema reset")

async def reset_group_schema():
    """Reset group database schema."""
    async with group_engine.begin() as conn:
        await conn.run_sync(GroupBase.metadata.drop_all)
    await init_group_db()
    print("✅ Group database schema reset")

async def reset_user_onboarding_schema():
    """Reset user onboarding database schema."""
    async with user_onboarding_engine.begin() as conn:
        await conn.run_sync(UserOnboardingBase.metadata.drop_all)
    await init_user_onboarding_db()
    print("✅ User onboarding database schema reset")

async def reset_group_onboarding_schema():
    """Reset group onboarding database schema."""
    async with group_onboarding_engine.begin() as conn:
        await conn.run_sync(GroupOnboardingBase.metadata.drop_all)
    await init_group_onboarding_db()
    print("✅ Group onboarding database schema reset")

async def reset_all_schemas():
    """Reset all database schemas."""
    await reset_personal_schema()
    await reset_group_schema()
    await reset_user_onboarding_schema()
    await reset_group_onboarding_schema()
    print("✅ All database schemas reset")

# ═══════════════════ BACKWARD COMPATIBILITY ═══════════════════
# Keep old names for backward compatibility with existing code
engine = personal_engine
AsyncSessionLocal = PersonalAsyncSessionLocal
Base = PersonalBase
init_db = init_personal_db
reset_schema = reset_personal_schema
