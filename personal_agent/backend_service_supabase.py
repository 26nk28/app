import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from supabase_db.supabase_client import get_supabase_client
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config import GEMINI_API_KEY

# Import our backend-specific prompt manager
from personal_agent.backend_manager import backend_prompt_manager, backend_json_parser

class BackendService:
    """Main backend service for processing user interactions"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY,
            model="gemini-2.5-flash-preview-05-20",
            temperature=0,
        )
        print("🔧 Backend service initialized")
        print(f"📁 Available backend prompts: {backend_prompt_manager.list_available_prompts()}")
    
    async def update_persona_smart(self, user_id: str, agent_id: str, current_persona: dict, new_message: str, timestamp: str):
        """Intelligently merge persona data using LLM"""
        print(f"🧠 Smart persona update for user: {user_id[:8]}...")
        
        try:
            # Use backend prompt manager
            merge_prompt = backend_prompt_manager.format_prompt(
                "persona_merge",
                current_persona=json.dumps(current_persona, indent=2),
                new_message=new_message,
                timestamp=timestamp
            )
            
            response = await self.llm.ainvoke(merge_prompt)
            response_text = response.content.strip()
            
            # Handle potential markdown formatting
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                json_start = 1
                json_end = len(lines)
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == "```":
                        json_end = i
                        break
                response_text = '\n'.join(lines[json_start:json_end]).strip()
            
            updated_persona = json.loads(response_text)
            print("✅ LLM merged persona:", updated_persona)
            
            # Save to Supabase
            supabase = get_supabase_client()
            result = supabase.table("persona").select("*").eq("user_id", user_id).eq("agent_id", agent_id).execute()
            
            if result.data:
                # Update existing persona
                supabase.table("persona").update({"data": updated_persona}).eq("user_id", user_id).eq("agent_id", agent_id).execute()
            else:
                # Create new persona
                persona_data = {
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "data": updated_persona
                }
                supabase.table("persona").insert(persona_data).execute()
            
            print("💾 Persona saved to database")
            return updated_persona
            
        except json.JSONDecodeError as e:
            print("⚠️ LLM returned invalid JSON for persona:", e)
            print("⚠️ Raw response:", response.content)
            return current_persona
        except Exception as e:
            print("⚠️ Persona update error:", e)
            return current_persona
    
    async def add_calendar_entry(self, user_id: str, agent_id: str, timestamp: str, info: str):
        """Add calendar entry with proper date/window calculation"""
        print(f"📅 Adding calendar entry for user: {user_id[:8]}...")
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Calculate window: 0→midnight-4am, 1→4-8am, 2→8am-noon, 3→noon-4pm, 4→4-8pm, 5→8pm-midnight
            window = dt.hour // 4
            
            entry_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "agent_id": agent_id,
                "date": dt.date().isoformat(),
                "window": window,
                "info": info
            }
            
            supabase = get_supabase_client()
            supabase.table("calendar_entries").insert(entry_data).execute()
            
            print(f"✅ Calendar entry saved: {dt.date()} window {window} ({dt.hour}:00) - {info}")
            return "calendar_entry_added"
            
        except Exception as e:
            print("⚠️ Calendar entry error:", e)
            return "calendar_entry_failed"
    
    async def process_interaction(self, interaction: dict, persona: dict, history: str):
        """Process a single interaction and determine actions"""
        print(f"🔄 Processing interaction: {interaction['input_by_user'][:50]}...")
        
        # Build context
        ctx = {
            "user_id": interaction['user_id'],
            "agent_id": interaction['agent_id'],
            "persona": persona,
            "history": history,
            "new_message": interaction['input_by_user'],
            "timestamp": interaction['timestamp'],
        }
        
        # Use backend prompt manager for decision making
        decision_prompt = backend_prompt_manager.format_prompt(
            "back_end_prompt",  # Using your existing prompt file name
            context=json.dumps(ctx, ensure_ascii=False, indent=2)
        )
        
        # Get LLM decision
        decision_response = await self.llm.ainvoke(decision_prompt)
        decision_text = decision_response.content.strip()
        
        print("🌐 Backend decision response:", decision_text[:100] + "..." if len(decision_text) > 100 else decision_text)
        
        # Parse actions using backend JSON parser
        actions = backend_json_parser.parse_gemini_json(decision_text)
        print("📋 Parsed backend actions:", actions)
        
        # Execute actions
        updated_persona = persona
        for action in actions:
            action_type = action.get("action")
            
            if action_type == "update_persona":
                print("🧠 Executing persona update...")
                updated_persona = await self.update_persona_smart(
                    user_id=interaction['user_id'],
                    agent_id=interaction['agent_id'],
                    current_persona=updated_persona,
                    new_message=interaction['input_by_user'],
                    timestamp=interaction['timestamp']
                )
                
            elif action_type == "add_calendar":
                print("📅 Executing calendar add...")
                meal_info = action.get("meal_info", interaction['input_by_user'])
                await self.add_calendar_entry(
                    user_id=interaction['user_id'],
                    agent_id=interaction['agent_id'],
                    timestamp=interaction['timestamp'],
                    info=meal_info
                )
                
            elif action_type == "none":
                print("ℹ️ No backend action needed:", action.get("reason", ""))
                
            else:
                print("⚠️ Unknown backend action:", action_type)
        
        return updated_persona
    
    async def run_backend_loop(self, user_id: str, agent_id: str):
        """Main backend processing loop"""
        print(f"🔄 Backend loop started for user: {user_id[:8]}... agent: {agent_id[:8]}...")
        
        while True:
            try:
                supabase = get_supabase_client()
                
                # Fetch unprocessed interaction
                result = (supabase.table("interactions")
                         .select("*")
                         .eq("processed", False)
                         .order("timestamp")
                         .limit(1)
                         .execute())
                
                if not result.data:
                    await asyncio.sleep(2)
                    continue
                
                interaction = result.data[0]
                
                # Mark as processed
                supabase.table("interactions").update({"processed": True}).eq("id", interaction['id']).execute()
                
                # Get current context
                # Get persona
                persona_result = (supabase.table("persona")
                                .select("data")
                                .eq("user_id", user_id)
                                .eq("agent_id", agent_id)
                                .execute())
                
                persona = persona_result.data[0]['data'] if persona_result.data else {}
                
                # Get recent history
                history_result = (supabase.table("interactions")
                                .select("*")
                                .eq("user_id", user_id)
                                .eq("agent_id", agent_id)
                                .eq("processed", True)
                                .order("timestamp", desc=True)
                                .limit(5)
                                .execute())
                
                history = "\n".join(
                    f"User: {r['input_by_user']}  Agent: {r['output_by_model']}"
                    for r in reversed(history_result.data)
                ) if history_result.data else "No previous conversation"
                
                # Process the interaction
                await self.process_interaction(interaction, persona, history)
                
            except Exception as e:
                print("⚠️ Backend loop error:", e)
                import traceback
                traceback.print_exc()
                await asyncio.sleep(2)



    async def run_multi_user_backend_loop(self):
        """New backend processing loop - processes interactions from ALL users"""
        print(f"🔄 Multi-user backend loop started - monitoring ALL users...")
        
        while True:
            try:
                supabase = get_supabase_client()
                
                # Fetch ANY unprocessed interaction (not user-specific)
                result = (supabase.table("interactions")
                        .select("*")
                        .eq("processed", False)
                        .order("timestamp")
                        .limit(1)
                        .execute())
                
                if not result.data:
                    await asyncio.sleep(2)
                    continue
                
                interaction = result.data[0]
                print(f"📝 Processing interaction from user: {interaction['user_id'][:8]}...")
                
                # Mark as processed
                supabase.table("interactions").update({"processed": True}).eq("id", interaction['id']).execute()
                
                # Get current context for THIS specific user
                current_user_id = interaction['user_id']
                current_agent_id = interaction['agent_id']
                
                # Get persona for the actual user
                persona_result = (supabase.table("persona")
                                .select("data")
                                .eq("user_id", current_user_id)
                                .eq("agent_id", current_agent_id)
                                .execute())
                
                persona = persona_result.data[0]['data'] if persona_result.data else {}
                
                # Get recent history for the actual user
                history_result = (supabase.table("interactions")
                                .select("*")
                                .eq("user_id", current_user_id)
                                .eq("agent_id", current_agent_id)
                                .eq("processed", True)
                                .order("timestamp", desc=True)
                                .limit(5)
                                .execute())
                
                history = "\n".join(
                    f"User: {r['input_by_user']}  Agent: {r['output_by_model']}"
                    for r in reversed(history_result.data)
                ) if history_result.data else "No previous conversation"
                
                # Process the interaction
                await self.process_interaction(interaction, persona, history)
                
            except Exception as e:
                print("⚠️ Multi-user backend loop error:", e)
                import traceback
                traceback.print_exc()
                await asyncio.sleep(2)

# New entry point function for multi-user backend


# Add this new function to your backend_service_supabase.py


async def run_multi_user_backend():
    """Entry point for multi-user backend service"""
    service = BackendService()
    await service.run_multi_user_backend_loop()


# Main execution
async def run_backend(user_id: str, agent_id: str):
    """Entry point for backend service"""
    service = BackendService()
    await service.run_backend_loop(user_id, agent_id)

if __name__ == "__main__":
    uid, aid = str(uuid.uuid4()), str(uuid.uuid4())
    print("🔄 Backend persona-updater started for", uid[:8], aid[:8])
    asyncio.run(run_backend(uid, aid))
