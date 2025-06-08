import asyncio
import json
from typing import List, Dict
from collections import defaultdict, Counter
from datetime import datetime, timedelta

# Import from personal_agent
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from personal_agent.db import AsyncSessionLocal as PersonalAgentDB
from personal_agent.models.persona import Persona
from personal_agent.models.calendar import CalendarEntry
from personal_agent.models.interaction import Interaction
from sqlalchemy import select, and_

class PersonaAggregator:
    """Aggregates persona data from multiple users for group recommendations"""
    
    async def aggregate_group_data(self, user_ids: List[str], agent_ids: List[str]) -> Dict:
        """Aggregate persona, calendar, and interaction data from all group members"""
        print(f"📊 Aggregating data for {len(user_ids)} group members...")
        
        aggregated_data = {
            'group_personas': [],
            'combined_preferences': {},
            'dietary_restrictions': [],
            'common_symptoms': [],
            'group_calendar_patterns': {},
            'recent_interactions': [],
            'compatibility_matrix': {}
        }
        
        # Collect data for each member
        for user_id, agent_id in zip(user_ids, agent_ids):
            member_data = await self._get_member_data(user_id, agent_id)
            aggregated_data['group_personas'].append(member_data)
        
        # Process and combine data
        aggregated_data['combined_preferences'] = self._combine_preferences(
            [member['persona'] for member in aggregated_data['group_personas']]
        )
        
        aggregated_data['dietary_restrictions'] = self._aggregate_dietary_restrictions(
            aggregated_data['group_personas']
        )
        
        aggregated_data['compatibility_matrix'] = self._calculate_compatibility_matrix(
            aggregated_data['group_personas']
        )
        
        aggregated_data['group_calendar_patterns'] = self._analyze_group_calendar_patterns(
            [member['calendar'] for member in aggregated_data['group_personas']]
        )
        
        print(f"✅ Data aggregation complete")
        return aggregated_data
    
    async def _get_member_data(self, user_id: str, agent_id: str) -> Dict:
        """Get comprehensive data for a single member"""
        async with PersonalAgentDB() as session:
            # Get persona
            persona_result = await session.execute(
                select(Persona).where(
                    and_(Persona.user_id == user_id, Persona.agent_id == agent_id)
                )
            )
            persona_row = persona_result.scalars().first()
            persona = persona_row.data if persona_row else {}
            
            # Get recent calendar entries (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            calendar_result = await session.execute(
                select(CalendarEntry).where(
                    and_(
                        CalendarEntry.user_id == user_id,
                        CalendarEntry.agent_id == agent_id,
                        CalendarEntry.date >= thirty_days_ago.date()
                    )
                ).order_by(CalendarEntry.date.desc())
            )
            calendar_entries = calendar_result.scalars().all()
            
            # Get recent interactions (last 10)
            interactions_result = await session.execute(
                select(Interaction).where(
                    and_(
                        Interaction.user_id == user_id,
                        Interaction.agent_id == agent_id,
                        Interaction.processed == True
                    )
                ).order_by(Interaction.timestamp.desc()).limit(10)
            )
            interactions = interactions_result.scalars().all()
            
            return {
                'user_id': user_id,
                'agent_id': agent_id,
                'persona': persona,
                'calendar': [{
                    'date': entry.date.isoformat(),
                    'window': entry.window,
                    'info': entry.info
                } for entry in calendar_entries],
                'recent_interactions': [{
                    'input': interaction.input_by_user,
                    'output': interaction.output_by_model,
                    'timestamp': interaction.timestamp.isoformat()
                } for interaction in interactions]
            }
    
    def _combine_preferences(self, personas: List[Dict]) -> Dict:
        """Combine food preferences from all members"""
        combined = {
            'likes': [],
            'dislikes': [],
            'allergies': [],
            'dietary_restrictions': [],
            'eating_patterns': {},
            'health_goals': []
        }
        
        for persona in personas:
            # Aggregate likes
            if 'preferences' in persona and 'likes' in persona['preferences']:
                combined['likes'].extend(persona['preferences']['likes'])
            
            # Aggregate dislikes
            if 'preferences' in persona and 'dislikes' in persona['preferences']:
                combined['dislikes'].extend(persona['preferences']['dislikes'])
            
            # Aggregate allergies
            if 'allergies' in persona:
                combined['allergies'].extend(persona['allergies'])
            
            # Aggregate dietary restrictions
            if 'dietary_restrictions' in persona:
                combined['dietary_restrictions'].extend(persona['dietary_restrictions'])
            
            # Aggregate eating patterns
            if 'eating_habits' in persona:
                combined['eating_patterns'][persona.get('user_id', 'unknown')] = persona['eating_habits']
        
        # Remove duplicates and count frequencies
        combined['likes'] = list(set(combined['likes']))
        combined['dislikes'] = list(set(combined['dislikes']))
        combined['allergies'] = list(set(combined['allergies']))
        combined['dietary_restrictions'] = list(set(combined['dietary_restrictions']))
        
        return combined
    
    def _aggregate_dietary_restrictions(self, group_personas: List[Dict]) -> List[Dict]:
        """Aggregate and prioritize dietary restrictions"""
        restrictions = []
        
        for member in group_personas:
            persona = member['persona']
            member_restrictions = {
                'user_id': member['user_id'],
                'allergies': persona.get('allergies', []),
                'dietary_restrictions': persona.get('dietary_restrictions', []),
                'intolerances': persona.get('intolerances', []),
                'severity': 'high'  # Default to high for safety
            }
            restrictions.append(member_restrictions)
        
        return restrictions
    
    def _calculate_compatibility_matrix(self, group_personas: List[Dict]) -> Dict:
        """Calculate food compatibility between group members"""
        compatibility = {}
        
        for i, member1 in enumerate(group_personas):
            user1_id = member1['user_id']
            compatibility[user1_id] = {}
            
            for j, member2 in enumerate(group_personas):
                user2_id = member2['user_id']
                
                if i == j:
                    compatibility[user1_id][user2_id] = 1.0
                else:
                    # Calculate compatibility score based on shared preferences
                    score = self._calculate_compatibility_score(
                        member1['persona'], member2['persona']
                    )
                    compatibility[user1_id][user2_id] = score
        
        return compatibility
    
    def _calculate_compatibility_score(self, persona1: Dict, persona2: Dict) -> float:
        """Calculate compatibility score between two personas"""
        score = 0.0
        factors = 0
        
        # Check shared likes
        likes1 = set(persona1.get('preferences', {}).get('likes', []))
        likes2 = set(persona2.get('preferences', {}).get('likes', []))
        if likes1 and likes2:
            shared_likes = len(likes1.intersection(likes2))
            total_likes = len(likes1.union(likes2))
            score += (shared_likes / total_likes) if total_likes > 0 else 0
            factors += 1
        
        # Check conflicting restrictions
        allergies1 = set(persona1.get('allergies', []))
        allergies2 = set(persona2.get('allergies', []))
        restrictions1 = set(persona1.get('dietary_restrictions', []))
        restrictions2 = set(persona2.get('dietary_restrictions', []))
        
        # Penalty for conflicting restrictions
        conflicts = len(allergies1.intersection(allergies2)) + len(restrictions1.intersection(restrictions2))
        if conflicts > 0:
            score -= 0.2 * conflicts
        
        factors += 1
        
        return max(0.0, min(1.0, score / factors if factors > 0 else 0.5))
    
    def _analyze_group_calendar_patterns(self, calendars: List[List[Dict]]) -> Dict:
        """Analyze eating patterns across group members"""
        patterns = {
            'common_meal_times': {},
            'frequent_foods': Counter(),
            'meal_frequency': defaultdict(int)
        }
        
        for calendar in calendars:
            for entry in calendar:
                # Analyze meal timing patterns
                window = entry['window']
                patterns['meal_frequency'][window] += 1
                
                # Extract food items from info
                info = entry['info'].lower()
                # Simple keyword extraction (could be enhanced with NLP)
                food_keywords = ['breakfast', 'lunch', 'dinner', 'snack', 'coffee', 'tea', 'fruit', 'vegetable']
                for keyword in food_keywords:
                    if keyword in info:
                        patterns['frequent_foods'][keyword] += 1
        
        return patterns
