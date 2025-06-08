import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from ..db import AsyncSessionLocal
from ..db.models import Group, GroupMember, GroupCalendar, MealSuggestion
from .persona_aggregator import PersonaAggregator
from .meal_recommender import MealRecommender

class GroupService:
    """Service for managing groups and their operations"""
    
    def __init__(self):
        self.persona_aggregator = PersonaAggregator()
        self.meal_recommender = MealRecommender()
    
    async def create_group(self, group_name: str, creator_user_id: str, creator_agent_id: str) -> str:
        """Create a new group and add creator as admin"""
        async with AsyncSessionLocal() as session:
            # Create group
            group = Group(
                id=str(uuid.uuid4()),
                name=group_name,
                created_at=datetime.now()
            )
            session.add(group)
            
            # Add creator as admin
            member = GroupMember(
                group_id=group.id,
                user_id=creator_user_id,
                agent_id=creator_agent_id,
                role='admin'
            )
            session.add(member)
            
            await session.commit()
            
            print(f"✅ Group '{group_name}' created with ID: {group.id[:8]}...")
            return group.id
    
    async def add_member_to_group(self, group_id: str, user_id: str, agent_id: str) -> bool:
        """Add a member to an existing group"""
        async with AsyncSessionLocal() as session:
            # Check if group exists and has space
            group = await session.get(Group, group_id)
            if not group or not group.is_active:
                print(f"❌ Group {group_id[:8]} not found or inactive")
                return False
            
            # Count current members
            member_count = await session.execute(
                select(GroupMember).where(
                    and_(GroupMember.group_id == group_id, GroupMember.is_active == True)
                )
            )
            current_members = len(member_count.scalars().all())
            
            if current_members >= group.max_members:
                print(f"❌ Group {group_id[:8]} is full ({current_members}/{group.max_members})")
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
                print(f"❌ User {user_id[:8]} already in group {group_id[:8]}")
                return False
            
            # Add member
            member = GroupMember(
                group_id=group_id,
                user_id=user_id,
                agent_id=agent_id,
                role='member'
            )
            session.add(member)
            await session.commit()
            
            print(f"✅ User {user_id[:8]} added to group {group_id[:8]}")
            return True
    
    async def get_group_members(self, group_id: str) -> List[Dict]:
        """Get all active members of a group"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupMember).where(
                    and_(GroupMember.group_id == group_id, GroupMember.is_active == True)
                )
            )
            members = result.scalars().all()
            
            return [{
                'user_id': member.user_id,
                'agent_id': member.agent_id,
                'role': member.role,
                'joined_at': member.joined_at
            } for member in members]
    
    async def generate_group_meal_suggestions(self, group_id: str) -> List[Dict]:
        """Generate meal suggestions for the group based on all members' preferences"""
        print(f"🍽️ Generating meal suggestions for group {group_id[:8]}...")
        
        # Get group members
        members = await self.get_group_members(group_id)
        if not members:
            print(f"❌ No members found for group {group_id[:8]}")
            return []
        
        # Aggregate all member personas and preferences
        aggregated_data = await self.persona_aggregator.aggregate_group_data(
            [member['user_id'] for member in members],
            [member['agent_id'] for member in members]
        )
        
        # Generate meal recommendations
        meal_suggestions = await self.meal_recommender.recommend_meals(
            aggregated_data, group_id
        )
        
        # Store suggestions in database
        await self._store_meal_suggestions(group_id, meal_suggestions)
        
        print(f"✅ Generated {len(meal_suggestions)} meal suggestions for group")
        return meal_suggestions
    
    async def _store_meal_suggestions(self, group_id: str, suggestions: List[Dict]):
        """Store meal suggestions in database"""
        async with AsyncSessionLocal() as session:
            for suggestion in suggestions:
                meal_suggestion = MealSuggestion(
                    group_id=group_id,
                    meal_name=suggestion['name'],
                    ingredients=suggestion['ingredients'],
                    dietary_compatibility=suggestion['compatible_members'],
                    nutrition_info=suggestion.get('nutrition', {}),
                    preparation_time=suggestion.get('prep_time', 30),
                    difficulty_level=suggestion.get('difficulty', 'medium')
                )
                session.add(meal_suggestion)
            
            await session.commit()
