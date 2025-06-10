from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(parent_dir))

from user_onboarding.services.onboarding_service import OnboardingService

router = APIRouter()

class UserOnboardingRequest(BaseModel):
    name: str
    email: str
    phone: str = None
    health_form: str

@router.post("/onboard")
async def onboard_user(request: UserOnboardingRequest):
    """Onboard a new user with single form submission"""
    
    if not request.name or not request.email or not request.health_form:
        raise HTTPException(status_code=400, detail="Name, email, and health_form are required")
    
    onboarding_service = OnboardingService()
    
    result = await onboarding_service.onboard_user(
        name=request.name,
        email=request.email,
        phone=request.phone,
        health_form=request.health_form
    )
    
    if result['success']:
        return {
            'message': result['message'],
            'onboarding_session_id': result['onboarding_session_id'],
            'user_id': result['user_id'],
            'agent_id': result['agent_id']
        }
    else:
        raise HTTPException(status_code=500, detail=result['message'])

@router.get("/status/{session_id}")
async def get_onboarding_status(session_id: str):
    """Get status of an onboarding session"""
    
    onboarding_service = OnboardingService()
    result = await onboarding_service.get_onboarding_status(session_id)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result
