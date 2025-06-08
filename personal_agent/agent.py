import asyncio
from pathlib import Path
from typing import TypedDict

from sqlalchemy import select
from personal_agent.db import AsyncSessionLocal
from personal_agent.models.user import User
from personal_agent.models.interaction import Interaction
from personal_agent.id_generator import generate_uuid4
from utils.config import GEMINI_API_KEY

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

# ─── User lookup/creation helper ────────────────────────────────────────────

async def get_or_create_user(name: str, email: str, phone: str = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            return user.user_id, user.agent_id
        uid, aid = generate_uuid4(), generate_uuid4()
        session.add(User(
            user_id=uid, agent_id=aid,
            name=name, email=email, phone=phone,
            health_form=None
        ))
        await session.commit()
        return uid, aid

# ─── Conversation state schema ──────────────────────────────────────────────

class HealthState(TypedDict):
    user_id: str
    agent_id: str
    last_question: str

# ─── Load system prompt ──────────────────────────────────────────────────────

PROMPT_FILE = Path(__file__).parent / "prompts" / "frontend" / "health_agent.txt"
SYSTEM_PROMPT = SystemMessagePromptTemplate.from_template(
    PROMPT_FILE.read_text(encoding="utf-8").strip()
)

# ─── Fetch last 10 interactions ──────────────────────────────────────────────

async def fetch_history(user_id: str, agent_id: str, limit: int = 10):
    async with AsyncSessionLocal() as session:
        q = (
            select(Interaction)
            .where(
                Interaction.user_id == user_id,
                Interaction.agent_id == agent_id
            )
            .order_by(Interaction.timestamp.desc())
            .limit(limit)
        )
        res = await session.execute(q)
        turns = res.scalars().all()
    return list(reversed(turns))

# ─── Node: ask_question ──────────────────────────────────────────────────────

async def ask_question(state: HealthState) -> dict:
    history = await fetch_history(state["user_id"], state["agent_id"])
    mem_text = "\n".join(
        f"You: {t.input_by_user}  Agent: {t.output_by_model}"
        for t in history
    )

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

# ─── Node: record_response (non-blocking input) ───────────────────────────────

async def record_response(state: HealthState) -> dict:
    """
    Reads the user's answer without blocking the event loop,
    logs it to the DB, and returns an empty dict.
    """
    answer = await asyncio.to_thread(input, "👤 You: ")
    answer = answer.strip()
    async with AsyncSessionLocal() as session:
        session.add(Interaction(
            id=generate_uuid4(),
            user_id=state["user_id"],
            agent_id=state["agent_id"],
            input_by_user=answer,
            output_by_model=state["last_question"]
        ))
        await session.commit()
        print(f"[DB] Recorded response for user {state['user_id']}")
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

# ─── Entrypoint ──────────────────────────────────────────────────────────────

async def run_frontend(user_id: str, agent_id: str):
    init_state: HealthState = {
        "user_id": user_id,
        "agent_id": agent_id,
        "last_question": ""
    }
    await graph.ainvoke(init_state)
