# run_backend.py

import asyncio
import logging

# Import your backend service
import personal_agent.backend_service_supabase as backend_service

# Hide SQLAlchemy INFO/DEBUG logs
logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

async def main():
    print("🔧 Starting FoodBuddy AI Backend Service...")
    print("=" * 50)
    print("🔄 Backend will continuously monitor for unprocessed interactions")
    print("📊 Processing interactions from ALL users in the database")
    print("⚡ Service ready - watching for new interactions...")
    print("   (Press Ctrl+C to stop)\n")
    
    try:
        # Use the new multi-user backend function
        await backend_service.run_multi_user_backend()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Backend service stopping...")
        print("✅ Backend service stopped cleanly!")

if __name__ == "__main__":
    asyncio.run(main())
