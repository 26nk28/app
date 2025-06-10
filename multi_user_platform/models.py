import sys
from pathlib import Path
from sqlalchemy import Column, String, DateTime, Integer, Boolean, JSON, Text
from datetime import datetime
import uuid

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import GroupBase from utils/db.py
from utils.db import GroupBase as Base

class Group(Base):
    __tablename__ = 'groups'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    max_users = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Group(id='{self.id[:8]}...', name='{self.name}')>"

class GroupMember(Base):
    __tablename__ = 'group_members'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)  # From personal_agent
    user_name = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    joined_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='member')  # 'admin', 'member'
    
    def __repr__(self):
        return f"<GroupMember(group_id='{self.group_id[:8]}...', user_name='{self.user_name}')>"
