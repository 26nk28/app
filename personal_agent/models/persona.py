# src/models/persona.py
from sqlalchemy import Column, String, JSON
from utils.db import (
    personal_engine as engine,
    PersonalAsyncSessionLocal as AsyncSessionLocal,
    PersonalBase as Base,
    init_personal_db as init_db,
    reset_personal_schema as reset_schema
)

# Re-export for existing code
__all__ = ['engine', 'AsyncSessionLocal', 'Base', 'init_db', 'reset_schema']


class Persona(Base):
    __tablename__ = "persona"

    user_id   = Column(String, primary_key=True)
    agent_id  = Column(String, unique=True)
    data      = Column(JSON, nullable=False)  # evolving persona JSON
