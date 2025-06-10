import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from utils.db import PersonalAsyncSessionLocal
from personal_agent.models.persona import Persona
from personal_agent.models.calendar import CalendarEntry
from sqlalchemy import select

class UserDataCache:
    """Background service that maintains in-memory cache of user personas and calendar data"""
    
    def __init__(self, refresh_interval: int = 60):
        """
        Args:
            refresh_interval: seconds between data refreshes (default: 60 seconds)
        """
        self.refresh_interval = refresh_interval
        self.cache: Dict[str, Dict] = {}  # user_id -> {"persona": ..., "calendar": ...}
        self._task: Optional[asyncio.Task] = None
        self._user_ids: List[str] = []
        self._running = False
        self._last_refresh: Dict[str, datetime] = {}
        
        print(f"🔄 UserDataCache initialized with {refresh_interval}s refresh interval")
    
    async def _fetch_persona(self, user_id: str) -> Dict:
        """Fetch latest persona data for a user"""
        async with PersonalAsyncSessionLocal() as session:
            result = await session.execute(
                select(Persona).where(Persona.user_id == user_id)
            )
            persona = result.scalars().first()
            if persona and persona.data:
                return persona.data
            return {}
    
    async def _fetch_calendar(self, user_id: str, days_back: int = 30) -> List[Dict]:
        """Fetch calendar entries for last N days"""
        async with PersonalAsyncSessionLocal() as session:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            result = await session.execute(
                select(CalendarEntry).where(
                    CalendarEntry.user_id == user_id,
                    CalendarEntry.date >= cutoff_date.date()
                ).order_by(CalendarEntry.date.desc(), CalendarEntry.window.desc())
            )
            
            entries = result.scalars().all()
            calendar_data = []
            
            for entry in entries:
                calendar_data.append({
                    'date': entry.date.isoformat(),
                    'window': entry.window,
                    'info': entry.info,
                    'created_at': entry.date.isoformat()  # For sorting
                })
            
            return calendar_data
    
    async def _refresh_user_data(self, user_id: str):
        """Refresh data for a single user"""
        try:
            print(f"🔄 Refreshing data for user {user_id[:8]}...")
            
            # Fetch persona and calendar data
            persona = await self._fetch_persona(user_id)
            calendar = await self._fetch_calendar(user_id)
            
            # Update cache
            self.cache[user_id] = {
                "persona": persona,
                "calendar": calendar,
                "last_updated": datetime.now().isoformat(),
                "calendar_entries_count": len(calendar)
            }
            
            self._last_refresh[user_id] = datetime.now()
            
            print(f"✅ Refreshed user {user_id[:8]}: "
                  f"persona={'✅' if persona else '❌'}, "
                  f"calendar={len(calendar)} entries")
            
        except Exception as e:
            print(f"❌ Error refreshing user {user_id[:8]}: {e}")
            # Keep old data if refresh fails
            if user_id not in self.cache:
                self.cache[user_id] = {
                    "persona": {},
                    "calendar": [],
                    "last_updated": datetime.now().isoformat(),
                    "error": str(e)
                }
    
    async def _refresh_loop(self):
        """Main background refresh loop"""
        print(f"🔄 Starting background refresh loop for {len(self._user_ids)} users")
        
        while self._running:
            if self._user_ids:
                print(f"🔄 Refreshing data for {len(self._user_ids)} users...")
                
                # Refresh all users
                for user_id in self._user_ids:
                    await self._refresh_user_data(user_id)
                    # Small delay between users to avoid overwhelming DB
                    await asyncio.sleep(1)
                
                print(f"✅ Completed refresh cycle for {len(self._user_ids)} users")
            else:
                print("⏳ No users to refresh, waiting...")
            
            # Wait for next refresh cycle
            await asyncio.sleep(self.refresh_interval)
    
    def start(self, user_ids: List[str]):
        """Start the background data loading for specified users"""
        if self._running:
            print("⚠️ UserDataCache already running, stopping previous instance")
            self.stop()
        
        self._user_ids = user_ids.copy()
        self._running = True
        self._task = asyncio.create_task(self._refresh_loop())
        
        print(f"🚀 Started UserDataCache for {len(user_ids)} users:")
        for user_id in user_ids:
            print(f"   - {user_id[:8]}...")
    
    def stop(self):
        """Stop the background data loading"""
        self._running = False
        if self._task:
            self._task.cancel()
            print("🛑 UserDataCache stopped")
    
    def add_user(self, user_id: str):
        """Add a new user to be tracked"""
        if user_id not in self._user_ids:
            self._user_ids.append(user_id)
            print(f"➕ Added user {user_id[:8]} to cache tracking")
    
    def remove_user(self, user_id: str):
        """Remove a user from tracking"""
        if user_id in self._user_ids:
            self._user_ids.remove(user_id)
            if user_id in self.cache:
                del self.cache[user_id]
            print(f"➖ Removed user {user_id[:8]} from cache tracking")
    
    def get_user_data(self, user_id: str) -> Optional[Dict]:
        """Get cached data for a user"""
        return self.cache.get(user_id, None)
    
    def get_user_persona(self, user_id: str) -> Dict:
        """Get just the persona data for a user"""
        user_data = self.cache.get(user_id, {})
        return user_data.get("persona", {})
    
    def get_user_calendar(self, user_id: str) -> List[Dict]:
        """Get just the calendar data for a user"""
        user_data = self.cache.get(user_id, {})
        return user_data.get("calendar", [])
    
    def get_all_cached_data(self) -> Dict:
        """Get all cached data"""
        return self.cache.copy()
    
    def get_cache_status(self) -> Dict:
        """Get status information about the cache"""
        status = {
            "running": self._running,
            "users_tracked": len(self._user_ids),
            "users_cached": len(self.cache),
            "last_refresh_times": {}
        }
        
        for user_id, last_refresh in self._last_refresh.items():
            status["last_refresh_times"][user_id[:8]] = last_refresh.isoformat()
        
        return status

# Global instance for the application
user_data_cache = UserDataCache(refresh_interval=60)  # Refresh every minute
