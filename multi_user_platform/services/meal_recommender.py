import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from utils.db import PersonalAsyncSessionLocal
from personal_agent.models.persona import Persona
from personal_agent.models.calendar import CalendarEntry
from multi_user_platform.services.group_service import GroupService
from sqlalchemy import select

from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config import GEMINI_API_KEY

class MealRecommendationService:
    """Service for generating meal recommendations using real user data"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY,
            model="gemini-2.5-flash-preview-05-20",
            temperature=0.3,
        )
        self.prompt_file = Path(__file__).parent.parent.parent /  "prompts" / "multi_agent"  / "meal_recommendation.txt"
    
    async def _fetch_user_persona_string(self, user_id: str) -> str:
        """Fetch persona as string for a user"""
        async with PersonalAsyncSessionLocal() as session:
            result = await session.execute(
                select(Persona).where(Persona.user_id == user_id)
            )
            persona = result.scalars().first()
            
            if persona and persona.data:
                # Convert persona data to string
                if isinstance(persona.data, dict):
                    return str(persona.data)
                else:
                    return str(persona.data)
            return "No persona data available"
    
    async def _fetch_user_calendar_string(self, user_id: str, days_back: int = 30) -> str:
        """Fetch calendar entries as string for last N days"""
        async with PersonalAsyncSessionLocal() as session:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            result = await session.execute(
                select(CalendarEntry).where(
                    CalendarEntry.user_id == user_id,
                    CalendarEntry.date >= cutoff_date.date()
                ).order_by(CalendarEntry.date.desc(), CalendarEntry.window.desc())
            )
            
            entries = result.scalars().all()
            
            if not entries:
                return "No recent meal history"
            
            # Convert calendar entries to readable string
            calendar_strings = []
            for entry in entries:
                calendar_strings.append(f"{entry.date} (window {entry.window}): {entry.info}")
            
            return "; ".join(calendar_strings)
    
    async def _load_group_data_fresh(self, group_id: str) -> List[Dict]:
        """Load fresh data for all group members (no caching)"""
        print(f"🔄 Loading fresh data for group {group_id[:8]}...")
        
        # Get group members
        members = await GroupService.get_group_members(group_id)
        
        if not members:
            raise ValueError(f"No members found in group {group_id[:8]}")
        
        # Load data for each member
        group_data = []
        
        for member in members:
            user_id = member['user_id']
            user_name = member['user_name']
            
            print(f"   📊 Loading data for {user_name} ({user_id[:8]}...)...")
            
            # Fetch persona and calendar as strings
            persona_string = await self._fetch_user_persona_string(user_id)
            calendar_string = await self._fetch_user_calendar_string(user_id, days_back=30)
            
            user_data = {
                'user_id': user_id,
                'name': user_name,
                'email': member['user_email'],
                'persona': persona_string,
                'calendar': calendar_string
            }
            
            group_data.append(user_data)
            print(f"   ✅ Loaded {user_name}: persona={len(persona_string)} chars, calendar={len(calendar_string)} chars")
        
        print(f"✅ Fresh data loaded for {len(group_data)} members")
        return group_data
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from file"""
        
        return self.prompt_file.read_text(encoding="utf-8")
        
    def _create_prompt(self, group_data: List[Dict]) -> str:
        """Create the complete prompt for Gemini"""
        template = self._load_prompt_template()
        
        # Build user data section
        user_data_section = ""
        for user in group_data:
            user_data_section += f"""
USER: {user['name']}
PERSONA: {user['persona']}
CALENDAR (last 30 days): {user['calendar']}

"""
        
        # Fill in the template
        prompt = template.format(user_data=user_data_section.strip())
        return prompt
    
    async def generate_recommendations(self, group_id: str) -> Dict:
        """Generate meal recommendations for a group using fresh data"""
        print(f"🍽️ Generating meal recommendations for group {group_id[:8]}...")
        
        try:
            # Load fresh data (no caching)
            group_data = await self._load_group_data_fresh(group_id)
            
            # Create prompt
            prompt = self._create_prompt(group_data)
            
            print(f"🤖 Sending request to Gemini...")
            print(f"   Prompt length: {len(prompt)} characters")
            
            # Get recommendations from Gemini
            response = await self.llm.ainvoke(prompt)
            response_text = response.content.strip()
            
            print(f"✅ Received response from Gemini")
            
            # Parse JSON response
            if response_text.startswith('```'):
                # Remove markdown formatting
                lines = response_text.split('\n')
                json_start = 1
                json_end = len(lines)
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '```':
                        json_end = i
                        break
                response_text = '\n'.join(lines[json_start:json_end]).strip()
            
            recommendations = json.loads(response_text)
            
            print(f"✅ Generated {len(recommendations.get('meal_options', []))} meal recommendations")
            
            # Add metadata
            result = {
                "group_id": group_id,
                "generated_at": datetime.now().isoformat(),
                "based_on_users": [user['name'] for user in group_data],
                "recommendations": recommendations
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
            # Return fallback recommendations
            return {
                "group_id": group_id,
                "generated_at": datetime.now().isoformat(),
                "error": str(e),
                "recommendations": {
                    
                }
            }
