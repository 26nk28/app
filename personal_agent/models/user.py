# src/models/user.py
from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.sqlite import TEXT
from personal_agent.db import Base

class User(Base):
    __tablename__ = "users"

    user_id   = Column(String, primary_key=True, index=True)
    agent_id  = Column(String, unique=True, index=True)
    name      = Column(String, nullable=False)
    email     = Column(String, unique=True, nullable=False)
    phone     = Column(String, nullable=True)
    health_form = Column(JSON, nullable=True)  # Store initial form JSON
