import sys
from pathlib import Path
from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from utils.db import UserOnboardingBase as Base

class UserOnboardingSession(Base):
    __tablename__ = 'user_onboarding_sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    health_form = Column(String, nullable=False)
    status = Column(String, default='completed')
    created_at = Column(DateTime, default=datetime.now)
    personal_agent_user_id = Column(String, nullable=True)
    personal_agent_agent_id = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<UserOnboardingSession(id='{self.id[:8]}...', name='{self.name}')>"
