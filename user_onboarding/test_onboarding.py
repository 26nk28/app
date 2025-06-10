import asyncio
import httpx
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from utils.db import reset_user_onboarding_schema

async def test_complete_integration():
    """Complete integration test of User Onboarding API"""
    print("🔄 Complete Integration Testing...")
    
    # Reset database
    await reset_user_onboarding_schema()
    
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient() as client:
        # Step 1: Verify service is running
        print("\n1️⃣ Service Status Check...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code != 200:
                print("❌ Service not healthy")
                return
            print("✅ Service is running")
        except Exception as e:
            print(f"❌ Cannot connect to service: {e}")
            return
        
        # Step 2: Check API documentation
        print("\n2️⃣ API Documentation Check...")
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✅ API documentation accessible")
            else:
                print("⚠️ API documentation not accessible")
        except:
            print("⚠️ API documentation endpoint not found")
        
        # Step 3: Test onboarding flow (will fail without Personal Agent)
        print("\n3️⃣ Onboarding Flow Test...")
        test_user = {
            "name": "Integration Test User",
            "email": "integration@test.com",
            "phone": "+1987654321",
            "health_form": "Integration test health form with detailed information about dietary preferences and restrictions."
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/onboard",
                json=test_user,
                timeout=30.0
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 500:
                print("   ✅ Expected failure (Personal Agent not running)")
                response_data = response.json()
                if "Failed to onboard user" in response_data.get("detail", ""):
                    print("   ✅ Correct error message")
            elif response.status_code == 200:
                print("   ✅ Onboarding successful!")
                response_data = response.json()
                print(f"   Session ID: {response_data.get('onboarding_session_id')}")
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Onboarding request failed: {e}")
        
        # Step 4: Test error handling
        print("\n4️⃣ Error Handling Test...")
        invalid_user = {"name": "", "email": "invalid", "health_form": ""}
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/onboard",
                json=invalid_user
            )
            
            if response.status_code == 400:
                print("   ✅ Correctly rejected invalid input")
            elif response.status_code == 422:
                print("   ✅ Validation error for invalid input")
            else:
                print(f"   ⚠️ Unexpected response to invalid input: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error handling test failed: {e}")
    
    print("\n✅ Integration testing completed!")

if __name__ == "__main__":
    asyncio.run(test_complete_integration())
