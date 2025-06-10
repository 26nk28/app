from sqlalchemy import Column, String, Date, Integer, ForeignKey
from utils.db import (
    personal_engine as engine,
    PersonalAsyncSessionLocal as AsyncSessionLocal,
    PersonalBase as Base,
    init_personal_db as init_db,
    reset_personal_schema as reset_schema
)

# Re-export for existing code
__all__ = ['engine', 'AsyncSessionLocal', 'Base', 'init_db', 'reset_schema']

class CalendarEntry(Base):
    __tablename__ = "calendar"
    id       = Column(String, primary_key=True)
    user_id  = Column(String, ForeignKey("users.user_id"), nullable=False)
    agent_id = Column(String, ForeignKey("users.agent_id"), nullable=False)
    date     = Column(Date, nullable=False)    # day of the entry
    window   = Column(Integer, nullable=False) # 0→midnight-4am, 1→4-8am, …
    info     = Column(String, nullable=False)  # what the user said about food/meals
