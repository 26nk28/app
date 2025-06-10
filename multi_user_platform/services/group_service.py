import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import select, and_

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# Import group database components
from utils.db import GroupAsyncSessionLocal, PersonalAsyncSessionLocal
from multi_user_platform.models import Group, GroupMember

# Import personal agent models for user verification
from personal_agent.models.user import User

class GroupService:
    """Service for managing groups with user verification"""
    
    @staticmethod
    async def verify_user_exists(user_id: str, user_name: str, user_email: str) -> bool:
        """Verify if user exists in personal database"""
        async with PersonalAsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(
                    and_(
                        User.user_id == user_id,
                        User.name == user_name,
                        User.email == user_email
                    )
                )
            )
            user = result.scalars().first()
            exists = user is not None
            
            if exists:
                print(f"✅ User {user_name} ({user_id[:8]}...) verified in personal database")
            else:
                print(f"❌ User {user_name} ({user_id[:8]}...) NOT found in personal database")
            
            return exists
    
    @staticmethod
    async def create_group(name: str) -> Dict:
        """Create a new group"""
        async with GroupAsyncSessionLocal() as session:
            group = Group(
                id=str(uuid.uuid4()),
                name=name,
                created_at=datetime.now(),
                max_users=3,
                is_active=True
            )
            session.add(group)
            await session.commit()
            
            print(f"✅ Group '{name}' created with ID: {group.id[:8]}...")
            
            return {
                'group_id': group.id,
                'group_name': name,
                'created_at': group.created_at.isoformat()
            }
    
    @staticmethod
    async def add_user_to_group(group_id: str, user_id: str, user_name: str, user_email: str) -> bool:
        """Add a user to an existing group (with verification)"""
        
        # FIRST: Verify user exists in personal database
        if not await GroupService.verify_user_exists(user_id, user_name, user_email):
            print(f"❌ Cannot add {user_name} to group: User not found in personal database")
            return False
        
        async with GroupAsyncSessionLocal() as session:
            # Check if group exists and has space
            group = await session.execute(
                select(Group).where(Group.id == group_id, Group.is_active == True)
            )
            group = group.scalars().first()
            
            if not group:
                print(f"❌ Group {group_id[:8]}... not found")
                return False
            
            # Check current member count
            member_count = await session.execute(
                select(GroupMember).where(
                    and_(GroupMember.group_id == group_id, GroupMember.is_active == True)
                )
            )
            current_members = len(member_count.scalars().all())
            
            if current_members >= group.max_users:
                print(f"❌ Group is full ({current_members}/{group.max_users})")
                return False
            
            # Check if user already in group
            existing_member = await session.execute(
                select(GroupMember).where(
                    and_(
                        GroupMember.group_id == group_id,
                        GroupMember.user_id == user_id,
                        GroupMember.is_active == True
                    )
                )
            )
            if existing_member.scalars().first():
                print(f"❌ User {user_name} already in group")
                return False
            
            # Add user to group
            group_member = GroupMember(
                id=str(uuid.uuid4()),
                group_id=group_id,
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                joined_at=datetime.now(),
                is_active=True,
                role='member'
            )
            session.add(group_member)
            await session.commit()
            
            print(f"✅ User {user_name} added to group successfully")
            return True
    
    @staticmethod
    async def get_group_members(group_id: str) -> List[Dict]:
        """Get all members of a group"""
        async with GroupAsyncSessionLocal() as session:
            members = await session.execute(
                select(GroupMember).where(
                    and_(GroupMember.group_id == group_id, GroupMember.is_active == True)
                )
            )
            
            member_list = []
            for member in members.scalars().all():
                member_list.append({
                    'user_id': member.user_id,
                    'user_name': member.user_name,
                    'user_email': member.user_email,
                    'role': member.role,
                    'joined_at': member.joined_at.isoformat()
                })
            
            return member_list
    
    @staticmethod
    async def get_all_users_from_personal_db() -> List[Dict]:
        """Get all users from personal database for reference"""
        async with PersonalAsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            user_list = []
            for user in users:
                user_list.append({
                    'user_id': user.user_id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone
                })
            
            return user_list
