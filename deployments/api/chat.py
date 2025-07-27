from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            
            if action == 'send_message':
                result = self.handle_send_message(data)
            elif action == 'get_history':
                result = self.handle_get_history(data)
            else:
                raise ValueError("Invalid action")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e)
            }
            
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_send_message(self, data):
        user_id = data.get('user_id')
        agent_id = data.get('agent_id')
        message = data.get('message')
        
        # Store user message in Supabase
        supabase = get_supabase_client()
        
        interaction_data = {
            "id": generate_uuid4(),
            "user_id": user_id,
            "agent_id": agent_id,
            "input_by_user": message,
            "output_by_model": "Processing...",
            "processed": False
        }
        
        result = supabase.table("interactions").insert(interaction_data).execute()
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "interaction_id": interaction_data["id"]
        }
    
    def handle_get_history(self, data):
        user_id = data.get('user_id')
        agent_id = data.get('agent_id')
        
        supabase = get_supabase_client()
        
        # Get conversation history
        response = (supabase.table("interactions")
                   .select("*")
                   .eq("user_id", user_id)
                   .eq("agent_id", agent_id)
                   .order("timestamp", desc=False)
                   .limit(20)
                   .execute())
        
        return {
            "success": True,
            "history": response.data
        }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
