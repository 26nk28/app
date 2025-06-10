import asyncio
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from multi_user_platform.services.meal_recommender import MealRecommendationService
from multi_user_platform.services.group_service import GroupService
from utils.db import reset_group_schema, PersonalAsyncSessionLocal
from personal_agent.models.user import User
from sqlalchemy import select

async def get_predefined_users():
    """Get the specific predefined users: Alice, Bob, Charlie"""
    predefined_names = ['Alice', 'Bob', 'Charlie']
    found_users = []
    
    async with PersonalAsyncSessionLocal() as session:
        for name in predefined_names:
            result = await session.execute(
                select(User).where(User.name == name)
            )
            user = result.scalars().first()
            
            if user:
                found_users.append({
                    'user_id': user.user_id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone
                })
                print(f"✅ Found predefined user: {name} ({user.user_id[:8]}...)")
            else:
                print(f"❌ Predefined user not found: {name}")
    
    return found_users

async def test_meal_recommendations_with_predefined_users():
    """Test meal recommendations with specifically Alice, Bob, and Charlie"""
    print("🧪 Testing Meal Recommendations with Predefined Users (Alice, Bob, Charlie)...")
    
    # Clean group database
    await reset_group_schema()
    
    # Get our specific predefined users
    predefined_users = await get_predefined_users()
    
    if len(predefined_users) < 3:
        print(f"❌ Only found {len(predefined_users)} out of 3 predefined users")
        print("💡 Make sure Alice, Bob, and Charlie exist in the database")
        print("💡 Run scripts/make_users.py to create them")
        return
    
    print(f"\n👥 Using predefined users:")
    for user in predefined_users:
        print(f"   - {user['name']} ({user['user_id'][:8]}...) - {user['email']}")
    
    # Create group with our predefined users
    group_info = await GroupService.create_group("Alice, Bob & Charlie Kitchen")
    group_id = group_info['group_id']
    
    # Add predefined users to group
    print(f"\n👥 Adding predefined users to group...")
    for user in predefined_users:
        success = await GroupService.add_user_to_group(
            group_id,
            user['user_id'],
            user['name'],
            user['email']
        )
        if success:
            print(f"✅ Added {user['name']} to group")
        else:
            print(f"❌ Failed to add {user['name']} to group")
    
    # Verify group composition
    members = await GroupService.get_group_members(group_id)
    print(f"\n📊 Final group composition ({len(members)} members):")
    for member in members:
        print(f"   - {member['user_name']} ({member['user_id'][:8]}...)")
    
    if len(members) != 3:
        print(f"❌ Expected 3 members, got {len(members)}")
        return
    
    # Generate meal recommendations
    print(f"\n🍽️ Generating meal recommendations for Alice, Bob & Charlie...")
    recommender = MealRecommendationService()
    
    result = await recommender.generate_recommendations(group_id)
    print(result)
    # Display results
    print(f"\n📋 MEAL RECOMMENDATIONS FOR ALICE, BOB & CHARLIE:")
    print(f"Group: {result.get('group_id', 'Unknown')[:8]}...")
    print(f"Generated at: {result.get('generated_at', 'Unknown')}")
    print(f"Based on users: {', '.join(result.get('based_on_users', []))}")
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    recommendations = result.get('recommendations', {})
    meal_options = recommendations.get('meal_options', [])
    
    print(f"\n🍽️ {len(meal_options)} MEAL OPTIONS:")
    for i, meal in enumerate(meal_options, 1):
        print(f"\n{i}. 🍽️ {meal.get('name', 'Unknown Meal')}")
        print(f"   📝 Description: {meal.get('description', 'No description')}")
        print(f"   👥 Suitable for: {', '.join(meal.get('suitable_for', []))}")
        print(f"   ⏰ Cooking time: {meal.get('cooking_time', 'Unknown')}")
        print(f"   💡 Why recommended: {meal.get('why_recommended', 'No explanation')}")
        
        ingredients = meal.get('ingredients', [])
        if ingredients:
            print(f"   🛒 Ingredients: {', '.join(ingredients[:5])}{'...' if len(ingredients) > 5 else ''}")
    
    # Show which meals work for which users
    print(f"\n👥 MEAL SUITABILITY BREAKDOWN:")
    user_names = [member['user_name'] for member in members]
    
    for user_name in user_names:
        suitable_meals = []
        for i, meal in enumerate(meal_options, 1):
            if user_name in meal.get('suitable_for', []):
                suitable_meals.append(f"Meal {i}")
        
        print(f"   {user_name}: {', '.join(suitable_meals) if suitable_meals else 'No specific meals'}")
    
    print(f"\n✅ Meal recommendation test completed for Alice, Bob & Charlie!")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_meal_recommendations_with_predefined_users())
    
    if result and 'error' not in result:
        print(f"\n🎉 SUCCESS: Generated recommendations for our predefined users!")
        meal_count = len(result.get('recommendations', {}).get('meal_options', []))
        print(f"📊 Total meals suggested: {meal_count}")
    else:
        print(f"\n❌ Test failed or encountered errors")
