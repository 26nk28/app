# src/models/interaction.py
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
from utils.db import (
    personal_engine as engine,
    PersonalAsyncSessionLocal as AsyncSessionLocal,
    PersonalBase as Base,
    init_personal_db as init_db,
    reset_personal_schema as reset_schema
)

# Re-export for existing code
__all__ = ['engine', 'AsyncSessionLocal', 'Base', 'init_db', 'reset_schema']
from sqlalchemy import Boolean

class Interaction(Base):
    __tablename__ = "interactions"

    id              = Column(String, primary_key=True, index=True)
    user_id         = Column(String, nullable=False, index=True)
    agent_id        = Column(String, nullable=False, index=True)
    input_by_user   = Column(String, nullable=False)
    output_by_model = Column(String, nullable=False)
    timestamp       = Column(
                        DateTime(timezone=True),
                        server_default=func.now()
                     )
    processed       = Column(Boolean, default=False, nullable=False)
