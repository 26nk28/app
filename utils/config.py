# utils/config.py

from pathlib import Path
import os

# ── Project root
BASE_DIR = Path(__file__).parent.parent.resolve()

# ── ADC credentials for Gemini (keep this pointing at your JSON)
CRED_PATH = BASE_DIR / "personal_agent" / "credentials" / "gemini-agent-462215-84ccb15bef8a.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CRED_PATH)

# ── Database settings
DB_PATH      = BASE_DIR / "data" / "users.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# ── Hard-coded Gemini API key (for now)
GEMINI_API_KEY = "AIzaSyA4yA9kIJum-1Uz0Hv8POst1dIok07Fln8"
