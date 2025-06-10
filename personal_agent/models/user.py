# src/models/user.py
from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.sqlite import TEXT
from utils.db import (
    personal_engine as engine,
    PersonalAsyncSessionLocal as AsyncSessionLocal,
    PersonalBase as Base,
    init_personal_db as init_db,
    reset_personal_schema as reset_schema
)

# Re-export for existing code
__all__ = ['engine', 'AsyncSessionLocal', 'Base', 'init_db', 'reset_schema']

class User(Base):
    __tablename__ = "users"

    user_id   = Column(String, primary_key=True, index=True)
    agent_id  = Column(String, unique=True, index=True)
    name      = Column(String, nullable=False)
    email     = Column(String, unique=True, nullable=False)
    phone     = Column(String, nullable=True)
    health_form = Column(String, nullable=True)  # Store initial form JSON
