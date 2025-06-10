import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from utils.db import GroupOnboardingAsyncSessionLocal
from group_onboarding.models.group_onboarding_models import GroupOnboardingSession
from group_onboarding.services.personal_agent_client import PersonalAgentClient
from group_onboarding.services.group_agent_client import GroupAgentClient

class GroupOnboardingService:
    """Service for handling group onboarding"""
    
    def __init__(self):
        self.personal_agent_client = PersonalAgentClient()
        self.group_agent_client = GroupAgentClient()
    
    async def create_group(self, group_name: str, creator_user_id: str, invited_user_ids: List[str]) -> Dict:
        """Create a new group with invited users"""
        
        # Verify creator exists
        creator_exists = await self.personal_agent_client.verify_user_exists(creator_user_id)
        if not creator_exists:
            return {
                'success': False,
                'error': f'Creator user {creator_user_id} not found in Personal Agent'
            }
        
        # Verify all invited users exist
        for user_id in invited_user_ids:
            user_exists = await self.personal_agent_client.verify_user_exists(user_id)
            if not user_exists:
                return {
                    'success': False,
                    'error': f'Invited user {user_id} not found in Personal Agent'
                }
        
        # Check total members (creator + invited) doesn't exceed limit
        total_members = 1 + len(invited_user_ids)
        if total_members > 3:
            return {
                'success': False,
                'error': f'Total members ({total_members}) exceeds maximum of 3'
            }
        
        # Create group onboarding session
        async with GroupOnboardingAsyncSessionLocal() as session:
            onboarding_session = GroupOnboardingSession(
                group_name=group_name,
                creator_user_id=creator_user_id,
                invited_user_ids=invited_user_ids,
                joined_user_ids=[creator_user_id],  # Creator automatically joins
                max_members=3,
                status='ready',  # Skip invitation process for now
                created_at=datetime.now()
            )
            session.add(onboarding_session)
            await session.commit()
            
            session_id = onboarding_session.id
            print(f"📝 Created group onboarding session: {session_id[:8]}...")
        
        try:
            # Create group in Group Agent with all members
            all_member_ids = [creator_user_id] + invited_user_ids
            print(f"🤖 Creating group in Group Agent with {len(all_member_ids)} members...")
            
            group_agent_response = await self.group_agent_client.create_group(
                group_name=group_name,
                creator_user_id=creator_user_id,
                member_user_ids=all_member_ids
            )
            
            group_id = group_agent_response['group_id']
            print(f"✅ Group created in Group Agent: {group_id[:8]}...")
            
            # Update onboarding session with success
            async with GroupOnboardingAsyncSessionLocal() as session:
                result = await session.get(GroupOnboardingSession, session_id)
                if result:
                    result.status = 'completed'
                    result.group_agent_group_id = group_id
                    result.joined_user_ids = all_member_ids
                    await session.commit()
            
            return {
                'success': True,
                'onboarding_session_id': session_id,
                'group_id': group_id,
                'group_name': group_name,
                'members': all_member_ids,
                'message': f'Group {group_name} created successfully with {len(all_member_ids)} members'
            }
            
        except Exception as e:
            print(f"❌ Error during group creation: {e}")
            
            # Update onboarding session with failure
            async with GroupOnboardingAsyncSessionLocal() as session:
                result = await session.get(GroupOnboardingSession, session_id)
                if result:
                    result.status = 'failed'
                    await session.commit()
            
            return {
                'success': False,
                'onboarding_session_id': session_id,
                'error': str(e),
                'message': f'Failed to create group {group_name}'
            }
    
    async def get_onboarding_status(self, session_id: str) -> Dict:
        """Get status of a group onboarding session"""
        async with GroupOnboardingAsyncSessionLocal() as session:
            result = await session.get(GroupOnboardingSession, session_id)
            
            if not result:
                return {'error': 'Group onboarding session not found'}
            
            return {
                'session_id': result.id,
                'group_name': result.group_name,
                'creator_user_id': result.creator_user_id,
                'invited_user_ids': result.invited_user_ids,
                'joined_user_ids': result.joined_user_ids,
                'status': result.status,
                'created_at': result.created_at.isoformat(),
                'group_id': result.group_agent_group_id,
                'total_members': len(result.joined_user_ids)
            }
