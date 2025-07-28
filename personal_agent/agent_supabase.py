import asyncio
from pathlib import Path
from typing import TypedDict
import os
from supabase_db.supabase_client import get_supabase_client
from utils.id_generator import generate_uuid4
# from utils.config import GEMINI_API_KEY

from langgraph.graph import StateGraph, START
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory.buffer_window import ConversationBufferWindowMemory
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# ─── User lookup/creation helper (converted to Supabase) ───────────────────

async def get_or_create_user(name: str, email: str, phone: str = None, health_form: str = None):
    """
    Get existing user or create new user with Supabase
    Returns: (user_id, agent_id)
    """
    supabase = get_supabase_client()
    
    try:
        # Check if user exists by email
        result = supabase.table("users").select("user_id, agent_id").eq("email", email).execute()
        
        if result.data:
            user = result.data[0]
            return user['user_id'], user['agent_id']
        
        # Create new user
        uid = generate_uuid4()
        aid = generate_uuid4()
        
        user_data = {
            "user_id": uid,
            "agent_id": aid,
            "name": name,
            "email": email,
            "phone": phone,
            "health_form": health_form
        }
        
        supabase.table("users").insert(user_data).execute()
        
        # Create persona
        persona_data = {
            "user_id": uid,
            "agent_id": aid,
            "data": health_form or {}
        }
        
        supabase.table("persona").insert(persona_data).execute()
        
        return uid, aid
        
    except Exception as error:
        print(f"❌ Error in get_or_create_user: {error}")
        raise error

# ─── Conversation state schema ──────────────────────────────────────────────

class HealthState(TypedDict):
    user_id: str
    agent_id: str
    last_question: str

# ─── Load system prompt ──────────────────────────────────────────────────────

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "frontend" / "health_agent.txt"
SYSTEM_PROMPT = SystemMessagePromptTemplate.from_template(
    PROMPT_FILE.read_text(encoding="utf-8").strip()
)

# ─── Fetch last 10 interactions (converted to Supabase) ─────────────────────

async def fetch_history(user_id: str, agent_id: str, limit: int = 10):
    supabase = get_supabase_client()
    
    try:
        response = (supabase.table("interactions")
                   .select("*")
                   .eq("user_id", user_id)
                   .eq("agent_id", agent_id)
                   .order("timestamp", desc=True)
                   .limit(limit)
                   .execute())
        
        interactions = list(reversed(response.data)) if response.data else []
        return interactions
        
    except Exception as error:
        print(f"❌ Error fetching history: {error}")
        return []

# ─── Node: ask_question ──────────────────────────────────────────────────────

async def ask_question(state: HealthState) -> dict:
    history = await fetch_history(state["user_id"], state["agent_id"])
    mem_text = "\n".join(
        f"You: {interaction['input_by_user']}  Agent: {interaction['output_by_model']}"
        for interaction in history
    )

    print(f"\n📝 Conversation history:\n{mem_text}\n")
    llm = ChatGoogleGenerativeAI(
        api_key=GEMINI_API_KEY,
        model="gemini-2.5-flash-preview-05-20",
        temperature=0.7
    )
    conv = ConversationChain(
        llm=llm,
        memory=ConversationBufferWindowMemory(
            memory_key="history", k=10, return_messages=True
        ),
        prompt=ChatPromptTemplate.from_messages([
            SYSTEM_PROMPT,
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    )

    question = await conv.apredict(input=mem_text or "Let's begin.")
    print(f"\n🤖 Agent: {question}\n")
    return {"last_question": question}

# ─── Node: record_response (converted to Supabase) ──────────────────────────

async def record_response(state: HealthState) -> dict:
    """
    Reads the user's answer without blocking the event loop,
    logs it to Supabase, and returns an empty dict.
    """
    answer = await asyncio.to_thread(input, "👤 You: ")
    answer = answer.strip()
    
    supabase = get_supabase_client()
    
    try:
        interaction_data = {
            "id": generate_uuid4(),
            "user_id": state["user_id"],
            "agent_id": state["agent_id"],
            "input_by_user": answer,
            "output_by_model": state["last_question"],
            "processed": False
        }
        
        supabase.table("interactions").insert(interaction_data).execute()
        print(f"[DB] Recorded response for user {state['user_id']}")
        
    except Exception as error:
        print(f"[DB] Error recording interaction: {error}")
    
    return {}

# ─── Build & compile the infinite loop StateGraph ───────────────────────────

graph = (
    StateGraph(HealthState)
    .add_node(ask_question)
    .add_node(record_response)
    .add_edge(START, ask_question.__name__)
    .add_edge(ask_question.__name__, record_response.__name__)
    .add_edge(record_response.__name__, ask_question.__name__)
    .compile()
)

# ─── Entrypoint (kept exactly the same) ──────────────────────────────────────

async def run_frontend(user_id: str, agent_id: str):
    init_state: HealthState = {
        "user_id": user_id,
        "agent_id": agent_id,
        "last_question": ""
    }
    await graph.ainvoke(init_state)
