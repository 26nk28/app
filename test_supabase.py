from supabase_db.supabase_client import get_supabase_client
import uuid
import json
from typing import Tuple, Optional

def generate_uuid4():
    """Generate UUID4 string"""
    return str(uuid.uuid4())

async def get_or_create_user(
    name: str, 
    email: str, 
    phone: str = None, 
    health_form: str = None
) -> Tuple[str, str]:
    """
    Get existing user or create new user with Supabase
    
    Args:
        name: User's full name
        email: User's email address (unique identifier)
        phone: Optional phone number
        health_form: Optional health form data (JSON string or dict)
    
    Returns:
        Tuple of (user_id, agent_id)
    
    Raises:
        Exception: If database operations fail
    """
    supabase = get_supabase_client()
    
    try:
        # Step 1: Check if user exists by email
        print(f"🔍 Checking for existing user with email: {email}")
        
        user_query = supabase.table("users").select("user_id, agent_id, name").eq("email", email)
        result = user_query.execute()
        
        if result.data:
            # User exists, return their IDs
            user = result.data[0]
            print(f"✅ Existing user found: {user['name']} ({email})")
            return user['user_id'], user['agent_id']
        
        print(f"👤 Creating new user: {name} ({email})")
        
        # Step 2: Generate new IDs
        uid = generate_uuid4()
        aid = generate_uuid4()
        
        # Step 3: Prepare health form data
        health_data = {}
        if health_form:
            if isinstance(health_form, str):
                try:
                    health_data = json.loads(health_form)
                except json.JSONDecodeError:
                    print("⚠️ Warning: Invalid JSON in health_form, storing as string")
                    health_data = {"raw_form": health_form}
            elif isinstance(health_form, dict):
                health_data = health_form
        
        # Step 4: Create user record
        user_data = {
            "user_id": uid,
            "agent_id": aid,
            "name": name,
            "email": email,
            "phone": phone,
            "health_form": health_form
        }
        
        user_result = supabase.table("users").insert(user_data).execute()
        
        if not user_result.data:
            raise Exception("Failed to insert user record")
        
        print(f"✅ User record created with ID: {uid}")
        
        # Step 5: Create persona record
        persona_data = {
            "user_id": uid,
            "agent_id": aid,
            "data": health_data
        }
        
        persona_result = supabase.table("persona").insert(persona_data).execute()
        
        if not persona_result.data:
            print("⚠️ Warning: User created but persona creation failed")
            # You might want to decide whether to rollback the user creation
            # or continue without the persona
        else:
            print(f"✅ Persona created for user: {uid}")
        
        print(f"🎉 New user successfully created: {name} ({email})")
        return uid, aid
        
    except Exception as error:
        print(f"❌ Error in get_or_create_user: {error}")
        raise error

# Test function
async def test_get_or_create_user():
    """Test the get_or_create_user function"""
    print("🧪 Testing get_or_create_user function...")
    
    # Test data
    test_users = [
        {
            "name": "Alice Johnson",
            "email": "alice.test@example.com",
            "phone": "+1234567890",
            "health_form": json.dumps({
                "age": 28,
                "allergies": ["nuts", "shellfish"],
                "dietary_preferences": ["vegetarian"],
                "medical_conditions": ["lactose_intolerant"]
            })
        },
        {
            "name": "Bob Smith",
            "email": "bob.test@example.com",
            "phone": "+0987654321",
            "health_form": json.dumps({
                "age": 35,
                "allergies": [],
                "dietary_preferences": ["keto"],
                "medical_conditions": ["diabetes"]
            })
        }
    ]
    
    for user in test_users:
        try:
            # First call - should create user
            uid1, aid1 = await get_or_create_user(**user)
            print(f"First call result: {uid1}, {aid1}")
            
            # Second call - should return existing user
            uid2, aid2 = await get_or_create_user(**user)
            print(f"Second call result: {uid2}, {aid2}")
            
            # Verify they're the same
            assert uid1 == uid2 and aid1 == aid2, "IDs should match for existing user"
            print(f"✅ Test passed for {user['email']}")
            
        except Exception as e:
            print(f"❌ Test failed for {user['email']}: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_get_or_create_user())
