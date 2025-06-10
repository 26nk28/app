import sys
from pathlib import Path
from sqlalchemy import Column, String, DateTime, JSON, Integer
from datetime import datetime
import uuid

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from utils.db import GroupOnboardingBase as Base

class GroupOnboardingSession(Base):
    __tablename__ = 'group_onboarding_sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_name = Column(String, nullable=False)
    creator_user_id = Column(String, nullable=False)
    invited_user_ids = Column(JSON, default=list)  # List of user IDs to invite
    joined_user_ids = Column(JSON, default=list)   # List of user IDs who joined
    max_members = Column(Integer, default=3)
    status = Column(String, default='created')  # 'created', 'inviting', 'ready', 'completed'
    created_at = Column(DateTime, default=datetime.now)
    group_agent_group_id = Column(String, nullable=True)  # Set after successful creation
    group_agent_id = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<GroupOnboardingSession(id='{self.id[:8]}...', name='{self.group_name}', status='{self.status}')>"
