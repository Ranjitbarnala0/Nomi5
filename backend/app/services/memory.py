
from typing import List, Dict, Any
from backend.app.services.openrouter import openrouter_service
from backend.app.services.supabase import supabase_service

class MemoryService:
    def __init__(self):
        pass  # No initialization needed, using openrouter_service singleton

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates a 768-dimensional vector for the given text.
        """
        try:
            return openrouter_service.embed_text(text)
        except Exception as e:
            print(f"Embedding Error: {e}")
            return []

    def store_memory(self, simulation_id: str, content: str, memory_type: str = "EPISODIC"):
        """
        Embeds and saves a new memory.
        """
        vector = self.get_embedding(content)
        if not vector:
            return # Skip if embedding failed

        client = supabase_service.get_client()
        client.table("memories").insert({
            "simulation_id": simulation_id,
            "content": content,
            "memory_type": memory_type,
            "embedding": vector
        }).execute()

    def retrieve_relevant_memories(self, simulation_id: str, query: str, limit: int = 5) -> List[str]:
        """
        Semantic Search: Finds memories conceptually related to the query.
        Uses the 'match_memories' RPC function in Supabase.
        """
        vector = self.get_embedding(query)
        if not vector:
            return []

        client = supabase_service.get_client()
        
        # Call the PostgreSQL function we defined in SQL
        response = client.rpc(
            "match_memories",
            {
                "query_embedding": vector,
                "match_threshold": 0.5, # Relevance threshold (0-1)
                "match_count": limit,
                "p_simulation_id": simulation_id
            }
        ).execute()

        # Extract just the text content
        return [item['content'] for item in response.data] if response.data else []

memory_service = MemoryService()
