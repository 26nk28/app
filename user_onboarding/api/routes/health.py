from fastapi import APIRouter
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(parent_dir))

from utils.db import UserOnboardingAsyncSessionLocal
from user_onboarding.services.personal_agent_client import PersonalAgentClient
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "user-onboarding"}

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependencies"""
    
    health_status = {
        "service": "user-onboarding",
        "status": "healthy",
        "checks": {}
    }
    
    # Check database
    try:
        async with UserOnboardingAsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check Personal Agent service
    try:
        client = PersonalAgentClient()
        is_healthy = await client.health_check()
        health_status["checks"]["personal_agent"] = {
            "status": "healthy" if is_healthy else "unhealthy"
        }
        if not is_healthy:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["personal_agent"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    return health_status
