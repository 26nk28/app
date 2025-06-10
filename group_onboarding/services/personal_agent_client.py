import httpx
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from utils.config import PERSONAL_AGENT_URL, INTER_SERVICE_API_KEY

class PersonalAgentClient:
    """Client to communicate with Personal Agent microservice"""
    
    def __init__(self):
        self.base_url = PERSONAL_AGENT_URL
        self.api_key = INTER_SERVICE_API_KEY
    
    async def verify_user_exists(self, user_id: str) -> bool:
        """Verify if user exists in Personal Agent service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/{user_id}",
                    headers={"X-API-Key": self.api_key},
                    timeout=10.0
                )
                return response.status_code == 200
            except:
                return False
    
    async def get_user_info(self, user_id: str):
        """Get user information from Personal Agent"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/{user_id}",
                    headers={"X-API-Key": self.api_key},
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except:
                return None
    
    async def health_check(self) -> bool:
        """Check if Personal Agent is healthy"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                return response.status_code == 200
            except:
                return False
