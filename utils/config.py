# utils/config.py

from pathlib import Path
import os

# ── Project root
BASE_DIR = Path(__file__).parent.parent.resolve()

# ── ADC credentials for Gemini (keep this pointing at your JSON)
CRED_PATH = BASE_DIR / "utils" / "gemini-agent-462215-84ccb15bef8a.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CRED_PATH)

# ── Personal Database settings
PERSONAL_DATABASE_DB_PATH = BASE_DIR / "data" / "users.db"
PERSONAL_DATABASE_URL = f"sqlite+aiosqlite:///{PERSONAL_DATABASE_DB_PATH}"

# ── Group database settings
GROUP_DB_PATH = BASE_DIR / "data" / "multi_user_platform.db"
GROUP_DATABASE_URL = f"sqlite+aiosqlite:///{GROUP_DB_PATH}"

# ── User Onboarding database settings
USER_ONBOARDING_DB_PATH = BASE_DIR / "data" / "user_onboarding.db"
USER_ONBOARDING_DATABASE_URL = f"sqlite+aiosqlite:///{USER_ONBOARDING_DB_PATH}"

# ── Group Onboarding database settings
GROUP_ONBOARDING_DB_PATH = BASE_DIR / "data" / "group_onboarding.db"
GROUP_ONBOARDING_DATABASE_URL = f"sqlite+aiosqlite:///{GROUP_ONBOARDING_DB_PATH}"

# ── Hard-coded Gemini API key (for now)
GEMINI_API_KEY = "AIzaSyA4yA9kIJum-1Uz0Hv8POst1dIok07Fln8"

# ── Service URLs for microservices communication

# ── API Keys for inter-service communication
INTER_SERVICE_API_KEY = "your-secret-api-key-here"  # Change in production
