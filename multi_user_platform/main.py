# TODO: implement main.py
import asyncio
import logging
from multi_user_platform.db import init_db
from multi_user_platform.services.group_service import GroupService
from .utils.config import DATABASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_test_scenario():
    """Create a test scenario with 3 users in a group"""
    
    print("🏗️ Setting up Multi-User Platform Test Scenario...")
    
    # Initialize database
    await init_db()
    
    # Create group service
    group_service = GroupService()
    
    # Simulate 3 users (these would come from personal_agent in real scenario)
    test_users = [
        {
            'user_id': 'user_001_alice',
            'agent_id': 'agent_001_alice',
            'name': 'Alice'
        },
        {
            'user_id': 'user_002_bob', 
            'agent_id': 'agent_002_bob',
            'name': 'Bob'
        },
        {
            'user_id': 'user_003_carol',
            'agent_id': 'agent_003_carol', 
            'name': 'Carol'
        }
    ]
    
    # Create group
    group_id = await group_service.create_group(
        group_name="Roommates Food Group",
        creator_user_id=test_users['user_id'],
        creator_agent_id=test_users['agent_id']
    )
    
    # Add other members
    for user in test_users[1:]:
        success = await group_service.add_member_to_group(
            group_id=group_id,
            user_id=user['user_id'],
            agent_id=user['agent_id']
        )
        if success:
            print(f"✅ Added {user['name']} to group")
    
    # Get group members
    members = await group_service.get_group_members(group_id)
    print(f"👥 Group has {len(members)} members")
    
    # Generate meal suggestions
    meal_suggestions = await group_service.generate_group_meal_suggestions(group_id)
    
    print(f"\n🍽️ Generated {len(meal_suggestions)} meal suggestions:")
    for i, meal in enumerate(meal_suggestions, 1):
        print(f"\n{i}. {meal['name']}")
        print(f"   Cuisine: {meal['cuisine_type']}")
        print(f"   Prep Time: {meal['prep_time']} minutes")
        print(f"   Difficulty: {meal['difficulty']}")
        print(f"   Compatible Members: {len(meal['compatible_members'])}/{len(members)}")
        if meal.get('incompatible_reasons'):
            print(f"   Restrictions: {meal['incompatible_reasons']}")
    
    return group_id, meal_suggestions

async def main():
    """Main entry point for multi-user platform"""
    try:
        group_id, suggestions = await create_test_scenario()
        print(f"\n✅ Multi-user platform test completed successfully!")
        print(f"📋 Group ID: {group_id}")
        print(f"🍽️ Generated {len(suggestions)} meal suggestions")
        
    except Exception as e:
        print(f"❌ Error in multi-user platform: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
