
from unittest.mock import MagicMock
import sys

# Mock Supabase
sys.modules['backend.app.services.supabase'] = MagicMock()
from backend.app.services.supabase import supabase_service
mock_client = MagicMock()
supabase_service.get_client.return_value = mock_client
mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = None

from backend.app.services.cortex import cortex_service
from backend.app.models.domain import DirectorOutput

def test_low_trust():
    print("\n--- Testing Low Trust (<50) ---")
    try:
        res = cortex_service.process_chat(
            'sim_low', 
            'Kiss me', 
            {'name':'Eva','core_wound':'Used','values_matrix':{}}, 
            {'emotional_bank_account':10}, 
            [], 
            []
        )
        print(f"Reaction: {res['director_log']['emotional_reaction']}")
        print(f"Response: {res['reply_text']}")
    except Exception as e:
        print(f"Error: {e}")

def test_high_trust():
    print("\n--- Testing High Trust (>=50) ---")
    try:
        res = cortex_service.process_chat(
            'sim_high', 
            'Kiss me', 
            {'name':'Eva','core_wound':'Used','values_matrix':{}}, 
            {'emotional_bank_account':80}, 
            [], 
            []
        )
        print(f"Reaction: {res['director_log']['emotional_reaction']}")
        print(f"Response: {res['reply_text']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_low_trust()
    test_high_trust()
