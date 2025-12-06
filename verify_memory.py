
from backend.app.services.memory import memory_service
import uuid

# Use a random UUID. 
# If the function exists, this should return [] (empty list).
# If the function does NOT exist, it will raise a Supabase/Postgrest error.
try:
    dummy_id = str(uuid.uuid4())
    print(f"Testing search with dummy ID: {dummy_id}")
    results = memory_service.retrieve_relevant_memories(dummy_id, "Hello world")
    print(f"Success! Result: {results}")
except Exception as e:
    print(f"Verification Failed: {e}")
