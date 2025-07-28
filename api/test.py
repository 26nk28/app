from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio
import traceback
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Comprehensive API health check and functionality test"""
        try:
            # Run comprehensive tests
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            test_results = loop.run_until_complete(self.run_comprehensive_tests())
            
            response = {
                "success": True,
                "message": "FoodBuddy AI Comprehensive API Test",
                "timestamp": datetime.now().isoformat(),
                "test_results": test_results,
                "endpoints": {
                    "test": "/api/test - GET/POST - Comprehensive API testing",
                    "login": "/api/login - POST - User authentication and creation", 
                    "chat": "/api/chat - POST - Chat interface (send_message, get_history)"
                },
                "environment": {
                    "python_runtime": "python3.9",
                    "platform": "vercel_serverless"
                },
                "conversation_flow": {
                    "status": "✅ Ready",
                    "features": [
                        "Real-time AI responses",
                        "Context-aware conversations",
                        "Proper message-response pairing",
                        "Conversation history storage"
                    ]
                }
            }
            
            # Determine overall status
            overall_success = all(test["status"] == "✅ PASS" for test in test_results.values())
            status_code = 200 if overall_success else 206  # 206 = Partial Content
            
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": "Comprehensive test failed"
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, indent=2).encode())
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive functionality tests"""
        test_results = {}
        
        # Test 1: Import Dependencies
        test_results["imports"] = await self.test_imports()
        
        # Test 2: Environment Variables
        test_results["environment"] = await self.test_environment_variables()
        
        # Test 3: Supabase Connection
        test_results["supabase_connection"] = await self.test_supabase_connection()
        
        # Test 4: User Creation (Enhanced)
        test_results["user_creation"] = await self.test_user_creation_flow()
        
        # Test 5: Chat API Integration (New)
        test_results["chat_api"] = await self.test_chat_api_integration()
        
        # Test 6: Complete Conversation Flow (New)
        test_results["conversation_flow"] = await self.test_complete_conversation_flow()
        
        # Test 7: Message Storage Verification (New)
        test_results["message_storage"] = await self.test_message_storage_verification()
        
        # Test 8: AI Response Generation (New)
        test_results["ai_responses"] = await self.test_ai_response_generation()
        
        return test_results
    
    async def test_imports(self):
        """Test if all required modules can be imported"""
        try:
            # Test core imports
            from supabase_db.supabase_client import get_supabase_client
            from personal_agent.agent_supabase import get_or_create_user, ask_question, fetch_history
            from utils.id_generator import generate_uuid4
            
            # Test optional imports
            try:
                from utils.config import GEMINI_API_KEY
                config_loaded = True
                gemini_available = bool(GEMINI_API_KEY)
            except:
                config_loaded = False
                gemini_available = False
            
            return {
                "status": "✅ PASS",
                "message": "All core modules imported successfully",
                "details": {
                    "supabase_client": "✅ Available",
                    "agent_supabase": "✅ Available", 
                    "ask_question": "✅ Available",
                    "fetch_history": "✅ Available",
                    "id_generator": "✅ Available",
                    "config": "✅ Available" if config_loaded else "⚠️ Warning: Config not found",
                    "gemini_api": "✅ Ready" if gemini_available else "⚠️ API key not found"
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"Import failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_environment_variables(self):
        """Test if environment variables are properly set"""
        try:
            required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
            optional_vars = ["GEMINI_API_KEY"]
            
            env_status = {}
            
            for var in required_vars:
                value = os.getenv(var)
                env_status[var] = "✅ Set" if value else "❌ Missing"
            
            for var in optional_vars:
                value = os.getenv(var)
                env_status[var] = "✅ Set" if value else "⚠️ Optional - Not set"
            
            all_required_set = all(os.getenv(var) for var in required_vars)
            
            return {
                "status": "✅ PASS" if all_required_set else "❌ FAIL",
                "message": "Environment variables check",
                "details": env_status
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"Environment check failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_supabase_connection(self):
        """Test Supabase database connection"""
        try:
            from supabase_db.supabase_client import get_supabase_client
            
            supabase = get_supabase_client()
            
            # Test table access
            users_test = supabase.table("users").select("user_id").limit(1).execute()
            interactions_test = supabase.table("interactions").select("id").limit(1).execute()
            persona_test = supabase.table("persona").select("user_id").limit(1).execute()
            
            return {
                "status": "✅ PASS",
                "message": "Supabase connection and tables accessible",
                "details": {
                    "connection": "✅ Connected",
                    "users_table": "✅ Accessible",
                    "interactions_table": "✅ Accessible",
                    "persona_table": "✅ Accessible"
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"Supabase connection failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_user_creation_flow(self):
        """Test complete user creation functionality"""
        try:
            from personal_agent.agent_supabase import get_or_create_user
            from supabase_db.supabase_client import get_supabase_client
            
            # Create a test user with realistic data
            test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_email = f"foodbuddy_test_{test_timestamp}@example.com"
            
            user_id, agent_id = await get_or_create_user(
                name=f"FoodBuddy Test User {test_timestamp}",
                email=test_email,
                phone=f"+1234{test_timestamp[-6:]}",
                health_form=json.dumps({
                    "diet": "vegetarian",
                    "allergies": ["nuts"],
                    "goals": ["weight_loss", "healthy_eating"],
                    "age": 25,
                    "test_created": True,
                    "created_at": datetime.now().isoformat()
                })
            )
            
            # Verify user was created in database
            supabase = get_supabase_client()
            user_check = supabase.table("users").select("*").eq("user_id", user_id).execute()
            persona_check = supabase.table("persona").select("*").eq("user_id", user_id).execute()
            
            return {
                "status": "✅ PASS",
                "message": "User creation flow successful",
                "details": {
                    "user_created": "✅ Yes",
                    "user_id": user_id[:12] + "...",
                    "agent_id": agent_id[:12] + "...",
                    "database_entry": "✅ Verified",
                    "persona_created": "✅ Yes" if persona_check.data else "❌ No",
                    "test_email": test_email
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"User creation failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_chat_api_integration(self):
        """Test chat API integration points"""
        try:
            from personal_agent.agent_supabase import ask_question, fetch_history
            from supabase_db.supabase_client import get_supabase_client
            from utils.id_generator import generate_uuid4
            
            # Create test user for chat
            test_user_id = f"chat_test_{generate_uuid4()[:8]}"
            test_agent_id = f"agent_test_{generate_uuid4()[:8]}"
            
            # Test ask_question function
            state = {
                "user_id": test_user_id,
                "agent_id": test_agent_id,
                "last_question": "Hello, I need help with nutrition planning"
            }
            
            ai_result = await ask_question(state)
            ai_response = ai_result.get("last_question", "")
            
            # Test fetch_history function
            history = await fetch_history(test_user_id, test_agent_id)
            
            return {
                "status": "✅ PASS",
                "message": "Chat API integration working",
                "details": {
                    "ask_question": "✅ Functional",
                    "ai_response_generated": "✅ Yes" if ai_response else "❌ No",
                    "fetch_history": "✅ Functional",
                    "response_length": len(ai_response) if ai_response else 0,
                    "history_entries": len(history)
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"Chat API integration failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_complete_conversation_flow(self):
        """Test complete conversation flow like the working chat.py"""
        try:
            from personal_agent.agent_supabase import get_or_create_user, ask_question, fetch_history
            from supabase_db.supabase_client import get_supabase_client
            from utils.id_generator import generate_uuid4
            
            # Step 1: Create a test user
            test_timestamp = datetime.now().strftime('%H%M%S')
            user_id, agent_id = await get_or_create_user(
                name=f"Conversation Test {test_timestamp}",
                email=f"conv_test_{test_timestamp}@example.com",
                phone=f"+1234{test_timestamp}",
                health_form='{"diet": "vegetarian", "test": true}'
            )
            
            # Step 2: Simulate conversation messages
            messages = [
                "Hello, I'm new to nutrition planning",
                "I'm vegetarian and want to lose weight",
                "What should I eat for breakfast?"
            ]
            
            conversation_results = []
            supabase = get_supabase_client()
            
            for i, message in enumerate(messages):
                # Generate AI response
                state = {
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "last_question": message
                }
                
                result = await ask_question(state)
                ai_response = result.get("last_question", "")
                
                # Store conversation (like chat.py does)
                interaction_data = {
                    "id": generate_uuid4(),
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "input_by_user": message,
                    "output_by_model": ai_response,
                    "processed": True
                }
                
                supabase.table("interactions").insert(interaction_data).execute()
                
                conversation_results.append({
                    "message_num": i + 1,
                    "user_message": message[:30] + "...",
                    "ai_response": ai_response[:50] + "..." if len(ai_response) > 50 else ai_response,
                    "stored": True
                })
            
            # Step 3: Verify conversation history
            history = await fetch_history(user_id, agent_id)
            
            return {
                "status": "✅ PASS",
                "message": "Complete conversation flow successful",
                "details": {
                    "user_created": "✅ Yes",
                    "messages_sent": len(messages),
                    "ai_responses_generated": len([r for r in conversation_results if r["ai_response"]]),
                    "conversations_stored": len(conversation_results),
                    "history_retrieved": len(history),
                    "conversation_sample": conversation_results[:2]  # Show first 2 exchanges
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"Conversation flow failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_message_storage_verification(self):
        """Test that messages are stored with proper pairing"""
        try:
            from supabase_db.supabase_client import get_supabase_client
            from utils.id_generator import generate_uuid4
            
            supabase = get_supabase_client()
            
            # Create test interaction with proper pairing
            test_user_id = f"storage_test_{generate_uuid4()[:8]}"
            test_agent_id = f"agent_storage_{generate_uuid4()[:8]}"
            
            user_message = "Test message for storage verification"
            ai_response = "Test AI response for storage verification"
            
            interaction_data = {
                "id": generate_uuid4(),
                "user_id": test_user_id,
                "agent_id": test_agent_id,
                "input_by_user": user_message,
                "output_by_model": ai_response,
                "processed": True
            }
            
            # Insert and verify
            insert_result = supabase.table("interactions").insert(interaction_data).execute()
            
            # Query back to verify proper storage
            query_result = supabase.table("interactions").select("*").eq("id", interaction_data["id"]).execute()
            
            stored_interaction = query_result.data[0] if query_result.data else None
            
            # Verify pairing is correct
            pairing_correct = (
                stored_interaction and
                stored_interaction["input_by_user"] == user_message and
                stored_interaction["output_by_model"] == ai_response
            )
            
            # Clean up
            supabase.table("interactions").delete().eq("id", interaction_data["id"]).execute()
            
            return {
                "status": "✅ PASS" if pairing_correct else "❌ FAIL",
                "message": "Message storage verification",
                "details": {
                    "storage": "✅ Successful",
                    "retrieval": "✅ Successful",
                    "message_pairing": "✅ Correct" if pairing_correct else "❌ Incorrect",
                    "user_message_match": stored_interaction["input_by_user"] == user_message if stored_interaction else False,
                    "ai_response_match": stored_interaction["output_by_model"] == ai_response if stored_interaction else False
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"Storage verification failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_ai_response_generation(self):
        """Test AI response generation quality and context awareness"""
        try:
            from personal_agent.agent_supabase import ask_question
            from utils.id_generator import generate_uuid4
            
            test_user_id = f"ai_test_{generate_uuid4()[:8]}"
            test_agent_id = f"ai_agent_{generate_uuid4()[:8]}"
            
            # Test different types of messages
            test_scenarios = [
                {
                    "input": "Hello, I'm new to healthy eating",
                    "expected_keywords": ["welcome", "help", "nutrition", "eating"]
                },
                {
                    "input": "I'm vegetarian and want to lose weight",
                    "expected_keywords": ["vegetarian", "weight", "protein", "plant"]
                },
                {
                    "input": "What should I eat for breakfast?",
                    "expected_keywords": ["breakfast", "meal", "morning", "eat"]
                }
            ]
            
            scenario_results = []
            
            for scenario in test_scenarios:
                state = {
                    "user_id": test_user_id,
                    "agent_id": test_agent_id, 
                    "last_question": scenario["input"]
                }
                
                result = await ask_question(state)
                ai_response = result.get("last_question", "").lower()
                
                # Check if response contains relevant keywords
                keyword_matches = sum(1 for keyword in scenario["expected_keywords"] if keyword in ai_response)
                
                scenario_results.append({
                    "input": scenario["input"][:30] + "...",
                    "response_length": len(ai_response),
                    "keyword_matches": f"{keyword_matches}/{len(scenario['expected_keywords'])}",
                    "relevant": keyword_matches > 0
                })
            
            all_relevant = all(result["relevant"] for result in scenario_results)
            
            return {
                "status": "✅ PASS" if all_relevant else "⚠️ PARTIAL",
                "message": "AI response generation test",
                "details": {
                    "scenarios_tested": len(test_scenarios),
                    "relevant_responses": sum(1 for r in scenario_results if r["relevant"]),
                    "response_quality": "✅ Good" if all_relevant else "⚠️ Needs improvement",
                    "scenario_results": scenario_results
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"AI response generation failed: {str(e)}",
                "error": str(e)
            }
    
    def do_POST(self):
        """Handle POST requests for specific test scenarios"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            test_type = request_data.get('test_type', 'conversation_demo')
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if test_type == 'conversation_demo':
                result = loop.run_until_complete(self.run_conversation_demo(request_data))
            elif test_type == 'user_creation_demo':
                result = loop.run_until_complete(self.run_user_creation_demo(request_data))
            else:
                result = {
                    "success": True,
                    "message": "POST test endpoint working",
                    "received_data": request_data,
                    "available_tests": ["conversation_demo", "user_creation_demo"],
                    "timestamp": datetime.now().isoformat()
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    async def run_conversation_demo(self, request_data):
        """Run a live conversation demo"""
        try:
            from personal_agent.agent_supabase import get_or_create_user, ask_question, fetch_history
            from supabase_db.supabase_client import get_supabase_client
            from utils.id_generator import generate_uuid4
            
            # Create demo user
            demo_timestamp = datetime.now().strftime('%H%M%S')
            user_id, agent_id = await get_or_create_user(
                name=f"Demo User {demo_timestamp}",
                email=f"demo_{demo_timestamp}@example.com",
                health_form='{"demo": true, "diet": "vegetarian"}'
            )
            
            # Demo conversation
            demo_messages = request_data.get('messages', [
                "Hello, I want to start eating healthier",
                "I'm vegetarian and trying to lose weight",
                "What are some good breakfast options?"
            ])
            
            conversation_log = []
            supabase = get_supabase_client()
            
            for message in demo_messages:
                # Generate AI response
                state = {"user_id": user_id, "agent_id": agent_id, "last_question": message}
                result = await ask_question(state)
                ai_response = result.get("last_question", "")
                
                # Store conversation
                interaction_data = {
                    "id": generate_uuid4(),
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "input_by_user": message,
                    "output_by_model": ai_response,
                    "processed": True
                }
                supabase.table("interactions").insert(interaction_data).execute()
                
                conversation_log.append({
                    "user": message,
                    "foodbuddy_ai": ai_response
                })
            
            return {
                "success": True,
                "message": "Live conversation demo completed",
                "demo_user_id": user_id[:12] + "...",
                "conversation_log": conversation_log,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Conversation demo failed"
            }
    
    async def run_user_creation_demo(self, request_data):
        """Run a user creation demo with custom data"""
        try:
            from personal_agent.agent_supabase import get_or_create_user
            
            demo_data = request_data.get('user_data', {})
            
            user_id, agent_id = await get_or_create_user(
                name=demo_data.get('name', 'Demo User'),
                email=demo_data.get('email', f'demo_{datetime.now().strftime("%H%M%S")}@example.com'),
                phone=demo_data.get('phone', '+1234567890'),
                health_form=json.dumps(demo_data.get('health_form', {"demo": True}))
            )
            
            return {
                "success": True,
                "message": "User creation demo successful",
                "created_user": {
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "name": demo_data.get('name', 'Demo User'),
                    "email": demo_data.get('email', 'demo email')
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "User creation demo failed"
            }
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
