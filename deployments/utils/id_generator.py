# src/id_generator.py
import uuid

def generate_uuid4() -> str:
    """Return a new UUID4 as a string."""
    return str(uuid.uuid4())
