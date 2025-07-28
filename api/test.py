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
        
        # Test 4: User Creation
        test_results["user_creation"] = await self.test_user_creation()
        
        # Test 5: Database Operations
        test_results["database_operations"] = await self.test_database_operations()
        
        # Test 6: Chat Functionality
        test_results["chat_functionality"] = await self.test_chat_functionality()
        
        # Test 7: Backend Integration Check
        test_results["backend_integration"] = await self.test_backend_integration()
        
        return test_results
    
    async def test_imports(self):
        """Test if all required modules can be imported"""
        try:
            # Test core imports
            from supabase_db.supabase_client import get_supabase_client
            from personal_agent.agent_supabase import get_or_create_user
            from utils.id_generator import generate_uuid4
            
            # Test optional imports
            try:
                from utils.config import GEMINI_API_KEY
                config_loaded = True
            except:
                config_loaded = False
            
            return {
                "status": "✅ PASS",
                "message": "All core modules imported successfully",
                "details": {
                    "supabase_client": "✅ Available",
                    "agent_supabase": "✅ Available", 
                    "id_generator": "✅ Available",
                    "config": "✅ Available" if config_loaded else "⚠️ Warning: Config not found"
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
            
            # Test basic connection by querying a table
            result = supabase.table("users").select("user_id").limit(1).execute()
            
            return {
                "status": "✅ PASS",
                "message": "Supabase connection successful",
                "details": {
                    "connection": "✅ Connected",
                    "database_accessible": "✅ Yes",
                    "query_test": "✅ Successful"
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"Supabase connection failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_user_creation(self):
        """Test user creation functionality"""
        try:
            from personal_agent.agent_supabase import get_or_create_user
            
            # Create a test user
            test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
            
            user_id, agent_id = await get_or_create_user(
                name="Test User",
                email=test_email,
                phone="+1234567890",
                health_form='{"test": true, "created_at": "' + datetime.now().isoformat() + '"}'
            )
            
            return {
                "status": "✅ PASS",
                "message": "User creation successful",
                "details": {
                    "user_created": "✅ Yes",
                    "user_id": user_id[:8] + "...",
                    "agent_id": agent_id[:8] + "...",
                    "test_email": test_email
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"User creation failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_database_operations(self):
        """Test basic database CRUD operations"""
        try:
            from supabase_db.supabase_client import get_supabase_client
            from utils.id_generator import generate_uuid4
            
            supabase = get_supabase_client()
            
            # Test: Insert interaction
            test_interaction = {
                "id": generate_uuid4(),
                "user_id": "test_user_new" + generate_uuid4()[:8],
                "agent_id": "test_agent_new" + generate_uuid4()[:8],
                "input_by_user": "Test message for API verification",
                "output_by_model": "Test response from API test",
                "processed": False
            }
            
            # Insert test interaction
            insert_result = supabase.table("interactions").insert(test_interaction).execute()
            
            # Query test interaction
            query_result = supabase.table("interactions").select("*").eq("id", test_interaction["id"]).execute()
            
            # Clean up - delete test interaction
            supabase.table("interactions").delete().eq("id", test_interaction["id"]).execute()
            
            return {
                "status": "✅ PASS",
                "message": "Database operations successful",
                "details": {
                    "insert": "✅ Successful",
                    "query": "✅ Successful", 
                    "cleanup": "✅ Completed",
                    "test_interaction_id": test_interaction["id"][:8] + "..."
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "message": f"Database operations failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_chat_functionality(self):
        """Test chat API functionality simulation"""
        try:
            from supabase_db.supabase_client import get_supabase_client
            from utils.id_generator import generate_uuid4
            
            supabase = get_supabase_client()
            
            # Create test user for chat
            test_user_id = "chat_test_" + generate_uuid4()[:8] 
            test_agent_id = "agent_test_" + generate_uuid4()[:8]
            
            # Simulate sending a message
            chat_interaction = {
                "id": generate_uuid4(),
                "user_id": test_user_id,
                "agent_id": test_agent_id,
                "input_by_user": "Hello, I need healthy meal suggestions",
                "output_by_model": "I'd be happy to help with meal suggestions! pLEASE wait",
                "processed": False
            }
            
            # Insert chat message
            supabase.table("interactions").insert(chat_interaction).execute()
            
            # Simulate getting chat history
            history_result = (supabase.table("interactions")
                            .select("*")
                            .eq("user_id", test_user_id)
                            .eq("agent_id", test_agent_id)
                            .execute())
            
            # Clean up
            supabase.table("interactions").delete().eq("id", chat_interaction["id"]).execute()
            
            return {
                "status": "✅ PASS",
                "message": "Chat functionality test successful",
                "details": {
                    "message_send": "✅ Simulated successfully",
                    "history_retrieval": "✅ Working",
                    "test_user_id": test_user_id,
                    "messages_found": len(history_result.data)
                }
            }
            
        except Exception as e:
            return {
                "status": "❌ FAIL", 
                "message": f"Chat functionality test failed: {str(e)}",
                "error": str(e)
            }
    
    async def test_backend_integration(self):
        """Test if backend integration points are ready"""
        try:
            from supabase_db.supabase_client import get_supabase_client
            
            supabase = get_supabase_client()
            
            # Check for unprocessed interactions (backend queue)
            unprocessed_result = supabase.table("interactions").select("id").eq("processed", False).limit(5).execute()
            
            # Check persona table structure
            persona_result = supabase.table("persona").select("user_id, agent_id").limit(1).execute()
            
            return {
                "status": "✅ PASS",
                "message": "Backend integration ready",
                "details": {
                    "interactions_table": "✅ Accessible",
                    "persona_table": "✅ Accessible",
                    "unprocessed_queue": f"{len(unprocessed_result.data)} items",
                    "backend_ready": "✅ Yes (when laptop backend runs)"
                }
            }
            
        except Exception as e:
            return {
                "status": "⚠️ PARTIAL",
                "message": f"Backend integration check: {str(e)}",
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
            
            test_type = request_data.get('test_type', 'quick')
            
            if test_type == 'user_creation':
                # Test specific user creation with provided data
                result = self.test_specific_user_creation(request_data)
            elif test_type == 'chat_simulation':
                # Test chat with specific messages
                result = self.test_chat_simulation(request_data)
            else:
                result = {
                    "success": True,
                    "message": "POST test endpoint working",
                    "received_data": request_data,
                    "available_tests": ["user_creation", "chat_simulation"]
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
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
