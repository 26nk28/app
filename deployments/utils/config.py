# utils/config.py

from pathlib import Path
import os

# ── Project root
BASE_DIR = Path(__file__).parent.parent.resolve()

# ── ADC credentials for Gemini (keep this pointing at your JSON)
CRED_PATH = BASE_DIR / "utils" / "gemini-agent-462215-84ccb15bef8a.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CRED_PATH)


