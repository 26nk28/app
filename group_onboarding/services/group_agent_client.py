import httpx
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from utils.config import GROUP_AGENT_URL, INTER_SERVICE_API_KEY

class GroupAgentClient:
    """Client to communicate with Group Agent microservice"""
    
    def __init__(self):
        self.base_url = GROUP_AGENT_URL
        self.api_key = INTER_SERVICE_API_KEY
    
    async def create_group(self, group_name: str, creator_user_id: str, member_user_ids: list):
        """Create group in Group Agent service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/groups",
                    json={
                        "name": group_name,
                        "creator_user_id": creator_user_id,
                        "member_user_ids": member_user_ids
                    },
                    headers={"X-API-Key": self.api_key},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Group Agent returned {response.status_code}: {response.text}")
                    
            except httpx.RequestError as e:
                raise Exception(f"Failed to connect to Group Agent: {e}")
    
    async def health_check(self) -> bool:
        """Check if Group Agent is healthy"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                return response.status_code == 200
            except:
                return False
