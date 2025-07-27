from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import asyncio

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your actual functions
from personal_agent.agent_supabase import get_or_create_user

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract user data
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone', '')
            health_form = data.get('health_form', '{}')
            
            # Use your actual get_or_create_user function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            user_id, agent_id = loop.run_until_complete(
                get_or_create_user(name, email, phone, health_form)
            )
            
            response = {
                "success": True,
                "user_id": user_id,
                "agent_id": agent_id,
                "message": "User authenticated successfully"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
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
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
