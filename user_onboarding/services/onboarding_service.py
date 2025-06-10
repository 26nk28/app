import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from utils.db import UserOnboardingAsyncSessionLocal
from user_onboarding.models.onboarding_models import UserOnboardingSession
from user_onboarding.services.personal_agent_client import PersonalAgentClient

class OnboardingService:
    """Service for handling user onboarding"""
    
    def __init__(self):
        self.personal_agent_client = PersonalAgentClient()
    
    async def onboard_user(self, name: str, email: str, phone: str, health_form: str) -> Dict:
        """Complete user onboarding in one step"""
        
        # Create onboarding session record
        async with UserOnboardingAsyncSessionLocal() as session:
            onboarding_session = UserOnboardingSession(
                name=name,
                email=email,
                phone=phone,
                health_form=health_form,
                status='processing',
                created_at=datetime.now()
            )
            session.add(onboarding_session)
            await session.commit()
            
            session_id = onboarding_session.id
            print(f"📝 Created onboarding session: {session_id[:8]}...")
        
        try:
            # Create user in Personal Agent
            print(f"🤖 Creating user in Personal Agent...")
            personal_agent_response = await self.personal_agent_client.create_user(
                name=name,
                email=email,
                phone=phone,
                health_form=health_form
            )
            
            user_id = personal_agent_response['user_id']
            agent_id = personal_agent_response['agent_id']
            
            print(f"✅ User created in Personal Agent: {user_id[:8]}...")
            
            # Update onboarding session with success
            async with UserOnboardingAsyncSessionLocal() as session:
                result = await session.get(UserOnboardingSession, session_id)
                if result:
                    result.status = 'completed'
                    result.personal_agent_user_id = user_id
                    result.personal_agent_agent_id = agent_id
                    await session.commit()
            
            return {
                'success': True,
                'onboarding_session_id': session_id,
                'user_id': user_id,
                'agent_id': agent_id,
                'message': f'User {name} onboarded successfully'
            }
            
        except Exception as e:
            print(f"❌ Error during onboarding: {e}")
            
            # Update onboarding session with failure
            async with UserOnboardingAsyncSessionLocal() as session:
                result = await session.get(UserOnboardingSession, session_id)
                if result:
                    result.status = 'failed'
                    await session.commit()
            
            return {
                'success': False,
                'onboarding_session_id': session_id,
                'error': str(e),
                'message': f'Failed to onboard user {name}'
            }
    
    async def get_onboarding_status(self, session_id: str) -> Dict:
        """Get status of an onboarding session"""
        async with UserOnboardingAsyncSessionLocal() as session:
            result = await session.get(UserOnboardingSession, session_id)
            
            if not result:
                return {'error': 'Onboarding session not found'}
            
            return {
                'session_id': result.id,
                'name': result.name,
                'email': result.email,
                'status': result.status,
                'created_at': result.created_at.isoformat(),
                'user_id': result.personal_agent_user_id,
                'agent_id': result.personal_agent_agent_id
            }
