from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
import asyncio
import random
import threading
import time


# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from personal_agent.agent_supabase import ask_question, fetch_history, get_or_create_user


class ChatHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Check the endpoint path
            if self.path == '/login':
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.handle_login(data))
            elif self.path == '/chat' or self.path == '/':
                action = data.get('action')
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                if action == 'send_message':
                    result = loop.run_until_complete(self.handle_send_message(data))
                elif action == 'get_history':
                    result = loop.run_until_complete(self.handle_get_history(data))
                else:
                    raise ValueError("Invalid action")
            else:
                raise ValueError("Invalid endpoint")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"❌ Error: {e}")
            error_response = {
                "success": False,
                "error": str(e)
            }
            
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    async def handle_login(self, data):
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone', '')
        health_form = data.get('health_form', '{}')
        
        print(f"🧑 Creating/finding user: {name} ({email})")
        
        try:
            user_id, agent_id = await get_or_create_user(name, email, phone, health_form)
            
            print(f"✅ User ID: {user_id}")
            print(f"✅ Agent ID: {agent_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "agent_id": agent_id,
                "message": "User authenticated successfully",
                "name": name,
                "email": email
            }
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            raise e
    
    async def handle_send_message(self, data):
        user_id = data.get('user_id')
        agent_id = data.get('agent_id')
        message = data.get('message')
        
        print(f"💬 Received message from {user_id[:8]}...: {message}")
        
        # Step 1: Generate AI response using ask_question
        state = {
            "user_id": user_id,
            "agent_id": agent_id,
            "last_question": message  # Pass user message for context
        }
        
        result = await ask_question(state)
        print('the result is:', result)
        ai_response = result.get("last_question", "I'm here to help with your nutrition needs!")
        
        print(f"🤖 AI response: {ai_response}")
        
        # Step 2: Store conversation properly without modifying record_response
        await self.store_conversation_properly(user_id, agent_id, message, ai_response)
        
        return {
            "success": True,
            "message": "Conversation stored correctly with proper message-response pairing",
            "ai_response": ai_response
        }
    
    async def store_conversation_properly(self, user_id, agent_id, user_message, ai_response):
        """
        Store the conversation with correct user message → AI response pairing
        WITHOUT modifying the original record_response function
        """
        from supabase_db.supabase_client import get_supabase_client
        from utils.id_generator import generate_uuid4
        
        supabase = get_supabase_client()
        
        try:
            # Store the complete conversation turn with correct pairing
            interaction_data = {
                "id": generate_uuid4(),
                "user_id": user_id,
                "agent_id": agent_id,
                "input_by_user": user_message,  # Current user message
                "output_by_model": ai_response,  # AI response to THIS message
                "processed": True  # Mark as processed since we have both parts
            }
            
            supabase.table("interactions").insert(interaction_data).execute()
            print(f"💾 [Proper Storage] User: '{user_message[:50]}...' → AI: '{ai_response[:50]}...'")
            
        except Exception as error:
            print(f"💾 [Storage Error] {error}")
    
    async def handle_get_history(self, data):
        user_id = data.get('user_id')
        agent_id = data.get('agent_id')
        
        print(f"📜 Getting history for user: {user_id[:8]}...")
        
        history = await fetch_history(user_id, agent_id)
        
        print(f"📊 Found {len(history)} history entries")
        
        return {
            "success": True,
            "history": history
        }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def create_and_test_user():
    """Create random user and test conversation automatically"""
    import requests
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        print("\n" + "="*60)
        print("🚀 AUTOMATED TESTING STARTING")
        print("="*60)
        
        # Step 1: Create random user
        random_id = random.randint(1000, 9999)
        user_data = {
            "name": f"flowcheck_agai23n",
            "email": f"flowcheck_ag123ain@example.com",
            "phone": f"flow1213123231_again",
            "health_form": json.dumps({
                "diet": "vegetarian",
                "allergies": ["nuts"],
                "goals": ["weight_loss", "healthy_eating"],
                "age": 25,
                "activity_level": "moderate"
            })
        }
        
        print(f"\n1️⃣ Creating user: {user_data['name']} ({user_data['email']})")
        
        response = requests.post("http://localhost:8000/login",
            headers={"Content-Type": "application/json"},
            json=user_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ User creation failed: {response.status_code}")
            return
        
        data = response.json()
        user_id = data['user_id']
        agent_id = data['agent_id']
        
        print(f"✅ User created successfully!")
        print(f"   User ID: {user_id}")
        print(f"   Agent ID: {agent_id}")
        
        # Step 2: Test conversation
        messages = [
            "Hello, I'm new to nutrition planning and want to start eating healthier",
            "I'm vegetarian and allergic to nuts. I want to lose 10 pounds.",
            "What should I eat for breakfast?",
            "Any meal prep suggestions for the week?"
        ]
        
        for i, message in enumerate(messages, 1):
            print(f"\n{i+1}️⃣ Sending message: {message}")
            
            response = requests.post("http://localhost:8000/chat",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "send_message",
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "message": message
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('ai_response', 'No response')
                print(f"✅ Response received!")
                print(f"🤖 FoodBuddy AI: {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}")
            else:
                print(f"❌ Message failed: {response.status_code}")
            
            time.sleep(3)  # Small delay between messages
        
        # Step 3: Get conversation history
        print(f"\n{len(messages)+2}️⃣ Getting complete conversation history...")
        
        response = requests.post("http://localhost:8000/chat",
            headers={"Content-Type": "application/json"},
            json={
                "action": "get_history",
                "user_id": user_id,
                "agent_id": agent_id
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            print(f"✅ Retrieved {len(history)} conversation entries")
            
            print("\n📜 CONVERSATION SUMMARY:")
            print("-" * 40)
            for i, entry in enumerate(history[-6:], 1):  # Show last 6 entries
                user_msg = entry.get('input_by_user', 'N/A')
                ai_msg = entry.get('output_by_model', 'N/A')
                if user_msg != 'N/A':
                    print(f"\n{i}. 👤 User: {user_msg}")
                if ai_msg != 'N/A' and ai_msg != 'Processing...':
                    print(f"   🤖 AI: {ai_msg[:150]}{'...' if len(ai_msg) > 150 else ''}")
        else:
            print(f"❌ History retrieval failed: {response.status_code}")
        
        print("\n" + "="*60)
        print("🎉 AUTOMATED TESTING COMPLETED SUCCESSFULLY!")
        print(f"👤 User: {user_data['name']}")
        print(f"🆔 User ID: {user_id[:8]}...")
        print(f"🤖 Agent ID: {agent_id[:8]}...")
        print("✅ FoodBuddy AI conversation system is working!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Automated test failed: {e}")


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ChatHandler)
    
    print(f"🚀 Starting FoodBuddy AI Test Server on http://localhost:{port}")
    print("📡 Available endpoints:")
    print(f"   POST http://localhost:{port}/login - User creation")
    print(f"   POST http://localhost:{port}/chat - Chat conversation")
    print("\n⚡ Automated testing will start in 2 seconds...")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    # Start automated testing in a separate thread
    test_thread = threading.Thread(target=create_and_test_user)
    test_thread.daemon = True
    test_thread.start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
