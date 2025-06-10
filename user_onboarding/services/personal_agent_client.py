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
    
    async def create_user(self, name: str, email: str, phone: str, health_form: str):
        """Create user in Personal Agent service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/users",
                    json={
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "health_form": health_form
                    },
                    headers={"X-API-Key": self.api_key},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Personal Agent returned {response.status_code}: {response.text}")
                    
            except httpx.RequestError as e:
                raise Exception(f"Failed to connect to Personal Agent: {e}")
    
    async def health_check(self) -> bool:
        """Check if Personal Agent is healthy"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200
            except:
                return False
