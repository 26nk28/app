import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://<your-project-ref>.supabase.co"
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") or "<your-anon-key>"

# Create the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase_client():
    """Returns the Supabase client instance"""
    return supabase
