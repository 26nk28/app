from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personal_agent.agent_supabase import ask_question, fetch_history
from supabase_db.supabase_client import get_supabase_client
from utils.id_generator import generate_uuid4

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            action = data.get('action')
            
            # Run async functions in sync context for Vercel
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if action == 'send_message':
                result = loop.run_until_complete(self.handle_send_message(data))
            elif action == 'get_history':
                result = loop.run_until_complete(self.handle_get_history(data))
            else:
                raise ValueError("Invalid action")
            
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
        
        # Step 2: Store conversation properly
        await self.store_conversation_properly(user_id, agent_id, message, ai_response)
        
        return {
            "success": True,
            "message": "Conversation stored correctly with proper message-response pairing",
            "ai_response": ai_response,
            "interaction_id": self.last_interaction_id if hasattr(self, 'last_interaction_id') else None
        }
    
    async def store_conversation_properly(self, user_id, agent_id, user_message, ai_response):
        """
        Store the conversation with correct user message → AI response pairing
        WITHOUT modifying the original record_response function
        """
        supabase = get_supabase_client()
        
        try:
            # Store the complete conversation turn with correct pairing
            interaction_id = generate_uuid4()
            interaction_data = {
                "id": interaction_id,
                "user_id": user_id,
                "agent_id": agent_id,
                "input_by_user": user_message,  # Current user message
                "output_by_model": ai_response,  # AI response to THIS message
                "processed": False  # Mark as processed since we have both parts
            }
            
            supabase.table("interactions").insert(interaction_data).execute()
            self.last_interaction_id = interaction_id
            print(f"💾 [Proper Storage] User: '{user_message[:50]}...' → AI: '{ai_response[:50]}...'")
            
        except Exception as error:
            print(f"💾 [Storage Error] {error}")
    
    async def handle_get_history(self, data):
        user_id = data.get('user_id')
        agent_id = data.get('agent_id')
        
        print(f"📜 Getting history for user: {user_id[:8]}...")
        
        # Use your existing fetch_history function
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
