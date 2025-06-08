# src/models/persona.py
from sqlalchemy import Column, String, JSON
from personal_agent.db import Base


class Persona(Base):
    __tablename__ = "persona"

    user_id   = Column(String, primary_key=True)
    agent_id  = Column(String, unique=True)
    data      = Column(JSON, nullable=False)  # evolving persona JSON
