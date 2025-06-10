import asyncio
import random
import uuid
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports (go up one level from scripts/)
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Now import from the correct paths
from personal_agent.agent import get_or_create_user
import personal_agent.backend_service as backend_service
from utils.db import (
    personal_engine as engine,
    PersonalAsyncSessionLocal as AsyncSessionLocal,
    PersonalBase as Base,
    init_personal_db as init_db,
    reset_personal_schema as reset_schema
)

# Re-export for existing code
__all__ = ['engine', 'AsyncSessionLocal', 'Base', 'init_db', 'reset_schema']
from personal_agent.models.interaction import Interaction

# ULTRA-CONSERVATIVE rate limiting for Gemini free tier
RATE_LIMITS = {
    'max_concurrent': 1,  # Only 1 user at a time
    'delay_between_requests': 12,  # 12 seconds = 5 requests per minute (safe buffer)
    'delay_between_users': 60,  # 1 minute between users
    'delay_between_messages': 15,  # 15 seconds between messages
    'backend_processing_wait': 120  # 2 minutes for backend processing
}

# Reduced conversations to minimize API calls
USER_CONVERSATIONS = {
    1: [  # User 1 - Health conscious (reduced to 3 messages)
        "I feel bloated after eating dairy",
        "I have a severe peanut allergy",
        "I eat three healthy meals a day"
    ],
    2: [  # User 2 - Busy lifestyle (reduced to 3 messages)
        "I usually skip breakfast due to work",
        "I'm lactose intolerant",
        "I love spicy food but it gives me heartburn"
    ],
    3: [  # User 3 - Active lifestyle (reduced to 3 messages)
        "I'm vegetarian and love it",
        "I have acid reflux issues",
        "I meal prep on Sundays"
    ]
}

# Simple health_form strings for each user
USER_HEALTH_FORMS = {
    1: "Health-conscious individual with dairy sensitivity and peanut allergy. Prefers organic foods, fruits, and vegetables. Eats 3 meals daily.",
    
    2: "Busy professional with lactose intolerance. Often skips breakfast due to work schedule. Enjoys spicy food but experiences heartburn.",
    
    3: "Vegetarian fitness enthusiast who meal preps regularly. Has acid reflux issues. Focuses on plant-based proteins."
}

async def add_interaction_to_db(user_id: str, agent_id: str, message: str):
    """Add interaction directly to database for processing"""
    async with AsyncSessionLocal() as session:
        interaction = Interaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            agent_id=agent_id,
            input_by_user=message,
            output_by_model="Understood, I'll note that in your profile.",
            processed=False,
            timestamp=datetime.now()
        )
        session.add(interaction)
        await session.commit()
        print(f"  💾 Added: {message[:50]}...")

async def simulate_user_conversation_ultra_safe(user_num: int, user_id: str, agent_id: str, user_name: str):
    """Ultra-safe conversation simulation with extreme rate limiting"""
    print(f"🗣️  Starting ULTRA-SAFE conversation for {user_name} (ID: {user_id[:8]}...)")
    
    # Get conversations for this user
    conversations = USER_CONVERSATIONS.get(user_num, USER_CONVERSATIONS[1])
    
    for i, message in enumerate(conversations):
        print(f"  👤 {user_name} says: {message}")
        
        # Add interaction to database
        await add_interaction_to_db(user_id, agent_id, message)
        
        # ULTRA-CONSERVATIVE rate limiting
        print(f"  ⏳ Ultra-safe wait: {RATE_LIMITS['delay_between_requests']}s for API safety...")
        await asyncio.sleep(RATE_LIMITS['delay_between_requests'])
        
        # Additional delay between messages
        if i < len(conversations) - 1:
            print(f"  ⏳ Message gap: {RATE_LIMITS['delay_between_messages']}s...")
            await asyncio.sleep(RATE_LIMITS['delay_between_messages'])
    
    print(f"✅ Finished ULTRA-SAFE conversation for {user_name}")
    return user_id, agent_id

async def make_users_ultra_safe(num_users: int = 3):  # Default to 2 users
    """Create users with ULTRA-SAFE sequential processing"""
    print(f"🚀 Creating {num_users} users with ULTRA-SAFE rate limiting...")
    print(f"⚠️  Using EXTREME rate limits: {RATE_LIMITS['delay_between_requests']}s between requests")
    print(f"⚠️  This will take approximately {(num_users * 3 * RATE_LIMITS['delay_between_requests'] + num_users * RATE_LIMITS['delay_between_users']) / 60:.1f} minutes")
    
    # Reset personal agent database
    
    await reset_schema()
    
    # Create users with simple health_form strings
    users = []
    user_names = ["Alice", "Bob", "Charlie"]
    
    for i in range(1, min(num_users + 1, 4)):  # Max 3 users defined
        user_name = user_names[i-1]
        email = f"{user_name.lower()}@example.com"
        phone = f"+1555000{i:04d}"
        health_form = USER_HEALTH_FORMS[i]
        
        # Use your actual function signature
        user_id, agent_id = await get_or_create_user(
            name=user_name,
            email=email,
            phone=phone,
            health_form=health_form
        )
        
        users.append((i, user_id, agent_id, user_name))
        print(f"👤 Created user {user_name} with user_id={user_id[:8]}...")
    
    # Process users ONE AT A TIME (completely sequential)
    for user_index, (i, user_id, agent_id, name) in enumerate(users):
        print(f"\n🎯 Processing user {user_index + 1}/{len(users)}: {name}")
        
        # Start backend for THIS user only
        print(f"🔄 Starting backend for {name}...")
        backend_task = asyncio.create_task(backend_service.run_backend(user_id, agent_id))
        
        # Wait for backend to initialize
        print(f"⏳ Waiting 10s for backend initialization...")
        await asyncio.sleep(10)
        
        # Run conversation for THIS user
        print(f"💬 Starting conversation for {name}...")
        await simulate_user_conversation_ultra_safe(i, user_id, agent_id, name)
        
        # Wait for backend to process all messages
        print(f"⏳ Waiting {RATE_LIMITS['backend_processing_wait']}s for backend processing...")
        await asyncio.sleep(RATE_LIMITS['backend_processing_wait'])
        
        # Stop backend for THIS user
        print(f"🛑 Stopping backend for {name}...")
        backend_task.cancel()
        try:
            await backend_task
        except asyncio.CancelledError:
            print(f"  ✅ Backend stopped for {name}")
        
        # Wait before next user (if not last user)
        if user_index < len(users) - 1:
            print(f"⏳ Waiting {RATE_LIMITS['delay_between_users']}s before next user...")
            await asyncio.sleep(RATE_LIMITS['delay_between_users'])
    
    # Return user information
    user_info = []
    for i, user_id, agent_id, name in users:
        user_info.append({
            'name': name,
            'user_id': user_id,
            'agent_id': agent_id,
            'hid': f"household_00{i}"
        })
    
    print(f"\n🎉 All {num_users} users completed with ULTRA-SAFE processing!")
    return user_info

async def verify_personas():
    """Verify that personas were created correctly"""
    print(f"\n🔍 Verifying created personas...")
    
    from personal_agent.models.persona import Persona
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        personas = await session.execute(select(Persona))
        persona_list = personas.scalars().all()
        
        print(f"📊 Found {len(persona_list)} personas:")
        for persona in persona_list:
            print(f"  👤 User {persona.user_id[:8]}...: {str(persona.data)[:100]}...")

async def main():
    """Main function with ultra-safe rate limiting"""
    print("🧪 Setting up users with ULTRA-SAFE rate limiting for Gemini free tier...")
    
    # Start with just 2 users to be extra safe
    num_users = 3
    user_info = await make_users_ultra_safe(num_users)
    
    # Verify personas were created
    await verify_personas()
    
    print(f"\n✅ ULTRA-SAFE setup complete! {num_users} users ready for group platform testing.")
    return user_info

if __name__ == "__main__":
    # Run with ultra-safe rate limiting
    user_data = asyncio.run(main())
    
    # Print final summary
    print(f"\n📝 SUMMARY - Users ready for group creation:")
    for user in user_data:
        print(f"  {user['name']} (hid: {user['hid']}): {user['user_id']}")
