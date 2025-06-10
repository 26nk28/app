from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(parent_dir))

from group_onboarding.services.group_onboarding_service import GroupOnboardingService

router = APIRouter()

class GroupCreationRequest(BaseModel):
    group_name: str
    creator_user_id: str
    invited_user_ids: List[str] = []

@router.post("/create-group")
async def create_group(request: GroupCreationRequest):
    """Create a new group with invited users"""
    
    if not request.group_name or not request.creator_user_id:
        raise HTTPException(status_code=400, detail="Group name and creator_user_id are required")
    
    # Validate invited users list
    if len(request.invited_user_ids) > 2:  # Creator + 2 invited = 3 total max
        raise HTTPException(status_code=400, detail="Maximum 2 users can be invited (3 total including creator)")
    
    onboarding_service = GroupOnboardingService()
    
    result = await onboarding_service.create_group(
        group_name=request.group_name,
        creator_user_id=request.creator_user_id,
        invited_user_ids=request.invited_user_ids
    )
    
    if result['success']:
        return {
            'message': result['message'],
            'onboarding_session_id': result['onboarding_session_id'],
            'group_id': result['group_id'],
            'group_name': result['group_name'],
            'members': result['members']
        }
    else:
        raise HTTPException(status_code=500, detail=result['message'])

@router.get("/status/{session_id}")
async def get_group_onboarding_status(session_id: str):
    """Get status of a group onboarding session"""
    
    onboarding_service = GroupOnboardingService()
    result = await onboarding_service.get_onboarding_status(session_id)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result
