import asyncio
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from multi_user_platform.services.user_data_loader import user_data_cache
from multi_user_platform.services.group_service import GroupService

class GroupDataManager:
    """Manages data loading for groups"""
    
    @staticmethod
    async def start_data_loading_for_group(group_id: str):
        """Start background data loading for all members of a group"""
        print(f"🔄 Starting data loading for group {group_id[:8]}...")
        
        # Get group members
        members = await GroupService.get_group_members(group_id)
        
        if not members:
            print(f"❌ No members found in group {group_id[:8]}")
            return False
        
        # Extract user IDs
        user_ids = [member['user_id'] for member in members]
        
        print(f"👥 Found {len(members)} members in group:")
        for member in members:
            print(f"   - {member['user_name']} ({member['user_id'][:8]}...)")
        
        # Start background data loading
        user_data_cache.start(user_ids)
        
        # Wait a moment for initial data load
        print("⏳ Waiting for initial data load...")
        await asyncio.sleep(5)
        
        # Verify data was loaded
        loaded_count = 0
        for user_id in user_ids:
            user_data = user_data_cache.get_user_data(user_id)
            if user_data:
                loaded_count += 1
                persona_status = "✅" if user_data.get("persona") else "❌"
                calendar_count = len(user_data.get("calendar", []))
                print(f"   📊 {user_id[:8]}: persona={persona_status}, calendar={calendar_count} entries")
        
        print(f"✅ Data loading started for {loaded_count}/{len(user_ids)} users")
        return loaded_count == len(user_ids)
    
    @staticmethod
    def get_group_aggregated_data(group_id: str) -> Dict:
        """Get aggregated data for all group members"""
        # This will be used by the meal recommendation service
        # For now, just return the raw cached data
        
        # Get all cached data
        all_data = user_data_cache.get_all_cached_data()
        
        aggregated = {
            "group_id": group_id,
            "members_data": all_data,
            "combined_personas": {},
            "combined_calendars": [],
            "dietary_restrictions": [],
            "common_preferences": []
        }
        
        # Combine personas and calendars
        for user_id, user_data in all_data.items():
            persona = user_data.get("persona", {})
            calendar = user_data.get("calendar", [])
            
            # Add to combined data
            aggregated["combined_personas"][user_id] = persona
            aggregated["combined_calendars"].extend([
                {**entry, "user_id": user_id} for entry in calendar
            ])
            
        #     # Extract dietary restrictions
        #     restrictions = persona.get("dietary_restrictions", [])
        #     if isinstance(restrictions, list):
        #         aggregated["dietary_restrictions"].extend(restrictions)
        
        # # Remove duplicates
        # aggregated["dietary_restrictions"] = list(set(aggregated["dietary_restrictions"]))
        
        return aggregated
    
    @staticmethod
    def stop_data_loading():
        """Stop background data loading"""
        user_data_cache.stop()
    
    @staticmethod
    def get_cache_status():
        """Get status of the data cache"""
        return user_data_cache.get_cache_status()
