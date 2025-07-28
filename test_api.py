import requests
import json

# Your deployed API base URL
BASE_URL = "https://app-seven-lime.vercel.app"

def test_health_check():
    """Test the API health check endpoint"""
    print("🔍 Testing API Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/test")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            data = response.json()
            print(f"   Tests passed: {sum(1 for test in data['test_results'].values() if test['status'] == '✅ PASS')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_user_creation():
    """Test user creation endpoint"""
    print("\n👤 Testing User Creation...")
    
    user_data = {
        "name": "Local Test User",
        "email": f"local.test.{hash('test') % 10000}@example.com",
        "phone": "+1234567890",
        "health_form": json.dumps({
            "diet": "vegetarian",
            "allergies": ["nuts"],
            "preferences": ["healthy", "organic"]
        })
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers={"Content-Type": "application/json"},
            json=user_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ User creation successful!")
                print(f"   User ID: {data['user_id'][:8]}...")
                print(f"   Agent ID: {data['agent_id'][:8]}...")
                return data['user_id'], data['agent_id']
            else:
                print(f"❌ User creation failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    return None, None

def test_chat_functionality(user_id, agent_id):
    """Test chat messaging functionality"""
    print("\n💬 Testing Chat Functionality...")
    
    # Test sending a message
    message_data = {
        "action": "send_message",
        "user_id": user_id,
        "agent_id": agent_id,
        "message": "Hello, I'm looking for healthy breakfast options that are vegetarian"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers={"Content-Type": "application/json"},
            json=message_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Message sent successfully!")
                print(f"   Interaction ID: {data.get('interaction_id', 'N/A')[:8]}...")
            else:
                print(f"❌ Message failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test getting chat history
    print("\n📜 Testing Chat History Retrieval...")
    
    history_data = {
        "action": "get_history",
        "user_id": user_id,
        "agent_id": agent_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers={"Content-Type": "application/json"},
            json=history_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                history = data.get("history", [])
                print(f"✅ Retrieved {len(history)} conversation entries")
                if history:
                    print(f"   Latest message: {history[-1].get('input_by_user', 'N/A')[:50]}...")
            else:
                print(f"❌ History retrieval failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    """Run comprehensive local API testing"""
    print("🚀 Testing FoodBuddy AI APIs from Local Machine")
    print("=" * 55)
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ Health check failed - stopping tests")
        return
    
    # Test 2: User creation
    user_id, agent_id = test_user_creation()
    if not user_id:
        print("❌ User creation failed - stopping chat tests")
        return
    
    # Test 3: Chat functionality
    test_chat_functionality(user_id, agent_id)
    
    print("\n" + "=" * 55)
    print("🎉 API testing completed!")
    print("\n💡 Next steps:")
    print("   1. Start your laptop backend: python -m personal_agent.run_backend")
    print("   2. Send more messages and watch them get processed")
    print("   3. Check Supabase dashboard for stored data")

if __name__ == "__main__":
    main()
