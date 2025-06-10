from fastapi import FastAPI
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from user_onboarding.api.routes import onboarding, health
from utils.db import init_user_onboarding_db

app = FastAPI(
    title="User Onboarding Service",
    description="Microservice for onboarding new users",
    version="1.0.0"
)

# Include routers
app.include_router(onboarding.router, prefix="/api/v1", tags=["onboarding"])
app.include_router(health.router, tags=["health"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_user_onboarding_db()
    print("🚀 User Onboarding Service started")

@app.get("/")
async def root():
    return {"message": "User Onboarding Service", "status": "running"}
