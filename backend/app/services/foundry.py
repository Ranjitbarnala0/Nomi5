import json
import re
from typing import Dict, Any, List
from backend.app.services.openrouter import openrouter_service
from backend.app.services.supabase import supabase_service
from backend.app.models.domain import UserVibe

class FoundryService:
    def generate_soul(self, user_vibe: UserVibe) -> Dict[str, Any]:
        """
        Generates the Immutable Core (Soul) of the Persona based on the User's Vibe.
        """
        system_prompt = f"""
        You are The Foundry, a psychological architect engine.
        Your task is to build a complex, flawed, realistic human persona ("Nomi") based on a user's psychometric profile.
        
        USER PROFILE:
        {user_vibe.model_dump_json()}
        
        MATCHING RULES:
        1. Strategy: {user_vibe.match_strategy} (e.g., if COMPLEMENTARY, balance their traits. If MIRROR, reflect them).
        2. Do NOT create a "perfect" partner. Create a human with a "Core Wound" and "Defense Mechanisms".
        3. The 'voice_texture' should be specific (e.g., "Raspy, fast-talker, uses 'literally' too much").
        4. The 'values_matrix' must include 0-10 scores for 'silence', 'money', 'loyalty', and 'independence'.
        
        OUTPUT SCHEMA (JSON ONLY):
        {{
            "name": "string",
            "appearance": "string (visual description)",
            "voice_texture": "string (auditory description)",
            "core_wound": "string (the root of their trauma)",
            "defense_mechanism": "string (how they protect the wound)",
            "attachment_style": "string (Secure, Anxious, Avoidant, or Fearful-Avoidant)",
            "values_matrix": {{ "silence": int, "money": int, "loyalty": int, "independence": int }},
            "sexual_orientation": "string"
        }}
        
        Generate the JSON now.
        """
        
        raw_response = openrouter_service.generate_text(system_prompt, temperature=0.85)
        clean_json = re.sub(r"```json|```", "", raw_response).strip()
        
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            raise ValueError(f"Foundry generation failed: {raw_response}")

    def generate_backstory(self, persona_core: Dict[str, Any]) -> List[str]:
        """
        Generates 5 specific 'Core Memories' based on the Persona's Core Wound.
        """
        system_prompt = f"""
        You are the Backstory Compiler.
        
        PERSONA:
        Name: {persona_core['name']}
        Core Wound: {persona_core['core_wound']}
        Defense Mechanism: {persona_core['defense_mechanism']}
        
        TASK:
        Write 5 distinct "Core Memories" that shaped this person.
        - One must be a childhood memory explaining the Core Wound.
        - One must be a recent memory showing their Defense Mechanism in action.
        - One must be a sensory memory (e.g., a specific smell or location).
        
        OUTPUT FORMAT:
        Return a simple JSON list of strings.
        ["Memory 1...", "Memory 2...", "Memory 3...", "Memory 4...", "Memory 5..."]
        """
        
        raw_response = openrouter_service.generate_text(system_prompt, temperature=0.8)
        clean_json = re.sub(r"```json|```", "", raw_response).strip()
        
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
             # Fallback: try to split by newlines if JSON fails
            return [line.strip() for line in raw_response.split('\n') if line.strip()]

    def embed_and_store_memories(self, simulation_id: str, memories: List[str]):
        """
        Embeds the text memories into vectors and stores them in Supabase.
        This enables the 'Dense' feeling where the AI remembers its past.
        """
        client = supabase_service.get_client()
        if not client:
             print("Skipping memory storage: Supabase client not initialized")
             return

        for memory_text in memories:
            # Generate Vector Embedding using OpenRouter
            vector = openrouter_service.embed_text(memory_text)
            
            # Insert into database
            client.table("memories").insert({
                "simulation_id": simulation_id,
                "content": memory_text,
                "memory_type": "CORE",
                "embedding": vector
            }).execute()

    def create_simulation(self, user_vibe: UserVibe, persona_data: Dict[str, Any]) -> str:
        """
        Orchestrates the entire Genesis:
        1. DB Rows
        2. Backstory Generation
        3. Vector Embedding
        """
        client = supabase_service.get_client()
        if not client:
            raise RuntimeError("Supabase client is not available. Cannot create simulation.") # Fail fast if no DB

        # 1. Create Simulation Container
        sim_response = client.table("simulations").insert({
            "user_vibe": user_vibe.model_dump(),
            "status": "ACTIVE"
        }).execute()
        
        if not sim_response.data:
            raise RuntimeError("Failed to create simulation row")
            
        simulation_id = sim_response.data[0]["id"]
        
        # 2. Create Persona Core
        client.table("persona_core").insert({
            "simulation_id": simulation_id,
            "name": persona_data["name"],
            "appearance": persona_data["appearance"],
            "voice_texture": persona_data["voice_texture"],
            "core_wound": persona_data["core_wound"],
            "defense_mechanism": persona_data["defense_mechanism"],
            "attachment_style": persona_data["attachment_style"],
            "values_matrix": persona_data["values_matrix"],
            "sexual_orientation": persona_data["sexual_orientation"]
        }).execute()
        
        # 3. Initialize Fluid State
        client.table("fluid_states").insert({
            "simulation_id": simulation_id,
            "emotional_bank_account": 0,
            "arousal_level": 0,
            "intellectual_boredom": 0,
            "current_craving": "Neutral"
        }).execute()
        
        # 4. Generate and Embed Backstory (NEW STEP)
        memories = self.generate_backstory(persona_data)
        self.embed_and_store_memories(simulation_id, memories)
        
        return simulation_id

foundry_service = FoundryService()
