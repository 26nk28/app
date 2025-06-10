from fastapi import FastAPI
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from group_onboarding.api.routes import group_onboarding, health
from utils.db import init_group_onboarding_db

app = FastAPI(
    title="Group Onboarding Service",
    description="Microservice for creating and managing groups",
    version="1.0.0"
)

# Include routers
app.include_router(group_onboarding.router, prefix="/api/v1", tags=["group-onboarding"])
app.include_router(health.router, tags=["health"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_group_onboarding_db()
    print("🚀 Group Onboarding Service started")

@app.get("/")
async def root():
    return {"message": "Group Onboarding Service", "status": "running"}
