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
        
        # STEP 1: Store user message FIRST so it's available in conversation history
        user_interaction_id = await self.store_user_message_first(user_id, agent_id, message)
        
        # STEP 2: Generate AI response using ask_question (now it can see the new user message)
        state = {
            "user_id": user_id,
            "agent_id": agent_id,
            "last_question": ""  # Empty - let it read from updated history
        }
        
        result = await ask_question(state)
        print('the result is:', result)
        ai_response = result.get("last_question", "I'm here to help with your nutrition needs!")
        
        print(f"🤖 AI response: {ai_response}")
        
        # STEP 3: Update the user's interaction with the AI response
        await self.update_user_interaction_with_ai_response(user_interaction_id, ai_response)
        
        return {
            "success": True,
            "message": "Conversation stored correctly with proper message-response pairing",
            "ai_response": ai_response,
            "interaction_id": user_interaction_id
        }
    
    async def store_user_message_first(self, user_id, agent_id, user_message):
        """
        Store the user's message FIRST so it's immediately available in conversation history
        """
        supabase = get_supabase_client()
        
        try:
            # Store user message with placeholder AI response
            interaction_id = generate_uuid4()
            interaction_data = {
                "id": interaction_id,
                "user_id": user_id,
                "agent_id": agent_id,
                "input_by_user": user_message,
                "output_by_model": "Processing...",  # Placeholder
                "processed": False  # Will update this when we get AI response
            }
            
            supabase.table("interactions").insert(interaction_data).execute()
            print(f"💾 [Step 1] Stored user message: '{user_message[:50]}...'")
            
            return interaction_id
            
        except Exception as error:
            print(f"💾 [Storage Error Step 1] {error}")
            raise error
    
    async def update_user_interaction_with_ai_response(self, interaction_id, ai_response):
        """
        Update the stored interaction with the actual AI response
        """
        supabase = get_supabase_client()
        
        try:
            # Update the existing interaction with AI response
            supabase.table("interactions").update({
                "output_by_model": ai_response,
                "processed": True
            }).eq("id", interaction_id).execute()
            
            print(f"💾 [Step 2] Updated with AI response: '{ai_response[:50]}...'")
            
        except Exception as error:
            print(f"💾 [Storage Error Step 2] {error}")
            raise error
    
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
