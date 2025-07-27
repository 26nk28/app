# main_personal.py

import asyncio
import logging

# Import your user-agent functions from personal_agent.agent
from personal_agent.agent_supabase import get_or_create_user, run_frontend

# Hide SQLAlchemy INFO/DEBUG logs (keeping for any remaining legacy dependencies)
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

async def main():
    print("🚀 Starting FoodBuddy AI Frontend...")
    print("=" * 50)
    
    # Create or fetch your user
    user_id, agent_id = await get_or_create_user(
        name="Nitesh Kumar",
        email="26nk28@gmail.com",
        phone="+0000000000",
        health_form='{"likes": ["dairy", "veggies"], "dislikes": ["spicy_food"], "dietary_preferences": ["anything except beef"]}'
    )
    
    print(f"✅ User authenticated:")
    print(f"   🆔 User ID: {user_id[:8]}...")
    print(f"   🤖 Agent ID: {agent_id[:8]}...")
    print(f"   📝 Health form loaded\n")
    
    print("💬 Starting conversation interface...")
    print("   (Backend service should be running separately on your laptop)")
    print("   (Press Ctrl+C to exit)\n")
    
    # Run only the frontend conversation interface
    try:
        await run_frontend(user_id, agent_id)
    except KeyboardInterrupt:
        print(f"\n👋 Conversation ended for user {user_id[:8]}...")
        print("✅ Session completed!")

if __name__ == "__main__":
    asyncio.run(main())
