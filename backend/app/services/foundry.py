import json
import re
from typing import Dict, Any, List
from backend.app.services.openrouter import openrouter_service
from backend.app.services.supabase import supabase_service
from backend.app.models.domain import UserVibe

class FoundryService:
    """
    The Foundry - Generates unique personas and opening scenarios
    based on user calibration profiles.
    """
    
    def generate_dynamic_persona(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a COMPLETELY UNIQUE persona based on the user's calibration profile.
        No hardcoded names, locations, or occupations.
        """
        user_name = user_profile.get('name', 'User')
        user_age = user_profile.get('age', 25)
        user_gender = user_profile.get('gender', 'Unknown')
        archetype = user_profile.get('detected_archetype', 'The Observer')
        match_strategy = user_profile.get('match_strategy', 'COMPLEMENTARY')
        
        system_prompt = f"""
        You are The Foundry, a psychological architect.
        Create a UNIQUE, complex human character to match this user.
        
        USER PROFILE:
        - Name: {user_name}
        - Age: {user_age}
        - Gender: {user_gender}
        - Archetype: {archetype}
        - Strategy: {match_strategy}
        
        MATCHING RULES:
        1. If COMPLEMENTARY: Create someone who balances their traits.
        2. If CHALLENGE: Create someone who pushes their boundaries.
        3. Generate a COMPLETELY RANDOM name (not Nomi, not generic names).
        4. Generate a RANDOM occupation (not UX designer, be creative).
        5. Generate a RANDOM hometown (be specific - city and country).
        6. The character MUST have a deep "Core Wound" that explains their behavior.
        7. The "voice_texture" should be vivid (how they speak, verbal tics, tone).
        
        OUTPUT JSON ONLY:
        {{
            "name": "string (unique name matching their background)",
            "age": int (18-45),
            "gender": "string",
            "occupation": "string (creative, specific)",
            "hometown": "string (city, country)",
            "appearance": "string (detailed physical description)",
            "voice_texture": "string (how they speak, verbal tics)",
            "core_wound": "string (deep psychological trauma)",
            "defense_mechanism": "string (how they protect themselves)",
            "attachment_style": "Secure | Anxious | Avoidant | Fearful-Avoidant",
            "values_matrix": {{"silence": 0-10, "money": 0-10, "loyalty": 0-10, "independence": 0-10}},
            "sexual_orientation": "string",
            "personality_hook": "string (one sentence that captures them)"
        }}
        """
        
        raw_response = openrouter_service.generate_text(system_prompt, temperature=0.95)
        clean_json = re.sub(r"```json|```", "", raw_response).strip()
        
        try:
            persona = json.loads(clean_json)
            # Ensure required fields exist
            persona.setdefault('name', 'Unknown')
            persona.setdefault('appearance', 'Average appearance')
            persona.setdefault('voice_texture', 'Normal speaking voice')
            persona.setdefault('core_wound', 'Fear of abandonment')
            persona.setdefault('defense_mechanism', 'Emotional distance')
            persona.setdefault('attachment_style', 'Avoidant')
            persona.setdefault('values_matrix', {"silence": 5, "money": 5, "loyalty": 5, "independence": 5})
            persona.setdefault('sexual_orientation', 'Heterosexual')
            return persona
        except json.JSONDecodeError:
            raise ValueError(f"Foundry generation failed: {raw_response}")

    def generate_opening_scenario(self, persona: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """
        Generates a CINEMATIC, IMMERSIVE opening scene where the user first meets the persona.
        Uses the same 3-layer format as the chat (italics + dialogue + emojis).
        """
        user_name = user_profile.get('name', 'User')
        persona_name = persona.get('name', 'Unknown')
        persona_occupation = persona.get('occupation', 'artist')
        persona_hometown = persona.get('hometown', 'the city')
        persona_appearance = persona.get('appearance', '')
        persona_hook = persona.get('personality_hook', '')
        persona_voice = persona.get('voice_texture', '')
        
        system_prompt = f"""
        You are a MASTER STORYTELLER creating the FIRST MEETING scene between two people.
        
        ═══════════════════════════════════════════════════════════
        CHARACTER DETAILS
        ═══════════════════════════════════════════════════════════
        Name: {persona_name}
        Occupation: {persona_occupation}
        From: {persona_hometown}
        Appearance: {persona_appearance}
        Voice: {persona_voice}
        Personality: {persona_hook}
        
        User's Name: {user_name}
        
        ═══════════════════════════════════════════════════════════
        SCENE REQUIREMENTS
        ═══════════════════════════════════════════════════════════
        
        1. **UNIQUE SETTING** - NOT a generic cafe. Be creative:
           - A bookstore during a power outage
           - An empty museum at closing time
           - A rooftop bar as fireworks start
           - A delayed train at midnight
           - A record shop on a rainy afternoon
           - A laundromat at 2am
        
        2. **SECOND PERSON** - Write "You are standing in..." "You notice..."
        
        3. **SENSORY DETAILS** - Describe:
           - The lighting (dim, golden, flickering)
           - The sounds (rain, distant music, silence)
           - The smells (coffee, old books, cigarette smoke)
           - The textures (cold glass, worn leather seats)
        
        4. **SHOW {persona_name.upper()}:**
           - Physical description in the scene
           - What they're doing when first seen
           - Their body language (guarded? confident? nervous?)
           - A subtle detail that makes them memorable
        
        5. **END WITH FIRST WORDS:**
           - {persona_name} notices you and says something
           - The dialogue should have personality
           - Include 1-2 emojis naturally
        
        6. **LENGTH:** 3-4 paragraphs. Immersive but not overwhelming.
        
        ═══════════════════════════════════════════════════════════
        FORMAT EXAMPLE
        ═══════════════════════════════════════════════════════════
        
        *The small café in El Born is crowded, the air thick with roasted beans and the damp pavement outside from a morning drizzle. {persona_name} sits across from you at a wobbly wooden table, legs crossed—a subtle barrier. Their dark wavy hair is pulled into a messy bun, a few rebellious strands framing their face.*

        *They catch you looking and don't look away immediately, eyes narrowing slightly in assessment. They lift their cappuccino with both hands, taking a slow sip before setting it down.*

        "So..." they say, voice carrying a slight rasp. "You've been staring at your coffee for thirty seconds. Are you contemplating the meaning of life, or regretting meeting a stranger from the internet?" 😏

        *A small, dry smile appears, but it doesn't reach their eyes yet.*
        
        ═══════════════════════════════════════════════════════════
        NOW WRITE THE OPENING SCENE
        ═══════════════════════════════════════════════════════════
        """
        
        return openrouter_service.generate_text(system_prompt, temperature=0.95)

    def generate_soul(self, user_vibe: UserVibe) -> Dict[str, Any]:
        """
        Legacy method - now wraps generate_dynamic_persona.
        """
        # Convert UserVibe to profile dict
        profile = {
            "openness": user_vibe.openness,
            "neuroticism": user_vibe.neuroticism,
            "detected_archetype": user_vibe.detected_archetype,
            "match_strategy": user_vibe.match_strategy
        }
        return self.generate_dynamic_persona(profile)

    def generate_backstory(self, persona_core: Dict[str, Any]) -> List[str]:
        """
        Generates 5 specific 'Core Memories' based on the Persona's Core Wound.
        """
        system_prompt = f"""
        You are the Backstory Compiler.
        
        PERSONA:
        Name: {persona_core.get('name', 'Unknown')}
        Age: {persona_core.get('age', 25)}
        Occupation: {persona_core.get('occupation', 'Unknown')}
        Hometown: {persona_core.get('hometown', 'Unknown')}
        Core Wound: {persona_core.get('core_wound', 'Unknown')}
        Defense Mechanism: {persona_core.get('defense_mechanism', 'Unknown')}
        
        TASK:
        Write 5 distinct "Core Memories" that shaped this person.
        - One must be a childhood memory explaining the Core Wound.
        - One must be a recent memory showing their Defense Mechanism in action.
        - One must be a sensory memory (e.g., a specific smell or location).
        - Use their actual hometown and occupation in the memories.
        
        OUTPUT FORMAT:
        Return a simple JSON list of strings.
        ["Memory 1...", "Memory 2...", "Memory 3...", "Memory 4...", "Memory 5..."]
        """
        
        raw_response = openrouter_service.generate_text(system_prompt, temperature=0.8)
        clean_json = re.sub(r"```json|```", "", raw_response).strip()
        
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            return [line.strip() for line in raw_response.split('\n') if line.strip()]

    def embed_and_store_memories(self, simulation_id: str, memories: List[str]):
        """
        Embeds the text memories into vectors and stores them in Supabase.
        """
        client = supabase_service.get_client()
        if not client:
            print("Skipping memory storage: Supabase client not initialized")
            return

        for memory_text in memories:
            vector = openrouter_service.embed_text(memory_text)
            client.table("memories").insert({
                "simulation_id": simulation_id,
                "content": memory_text,
                "memory_type": "CORE",
                "embedding": vector
            }).execute()

    def create_simulation_from_calibration(
        self, 
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a complete simulation from a calibrated user profile.
        Returns simulation_id, persona, and opening scenario.
        """
        client = supabase_service.get_client()
        if not client:
            raise RuntimeError("Supabase client is not available.")

        # 1. Generate the unique persona
        persona = self.generate_dynamic_persona(user_profile)
        
        # 2. Generate the opening scenario
        opening_scenario = self.generate_opening_scenario(persona, user_profile)
        
        # 3. Create simulation with is_calibrated = True
        sim_response = client.table("simulations").insert({
            "user_vibe": user_profile,
            "user_profile": user_profile,
            "status": "ACTIVE",
            "is_calibrated": True,
            "calibration_step": 4,
            "opening_scenario": opening_scenario
        }).execute()
        
        if not sim_response.data:
            raise RuntimeError("Failed to create simulation row")
            
        simulation_id = sim_response.data[0]["id"]
        
        # 4. Create Persona Core
        client.table("persona_core").insert({
            "simulation_id": simulation_id,
            "name": persona.get("name", "Unknown"),
            "appearance": persona.get("appearance", ""),
            "voice_texture": persona.get("voice_texture", ""),
            "core_wound": persona.get("core_wound", ""),
            "defense_mechanism": persona.get("defense_mechanism", ""),
            "attachment_style": persona.get("attachment_style", "Avoidant"),
            "values_matrix": persona.get("values_matrix", {}),
            "sexual_orientation": persona.get("sexual_orientation", "Unknown")
        }).execute()
        
        # 5. Initialize Fluid State
        client.table("fluid_states").insert({
            "simulation_id": simulation_id,
            "emotional_bank_account": 0,
            "arousal_level": 0,
            "intellectual_boredom": 0,
            "current_craving": "Neutral"
        }).execute()
        
        # 6. Generate and embed backstory
        memories = self.generate_backstory(persona)
        self.embed_and_store_memories(simulation_id, memories)
        
        return {
            "simulation_id": simulation_id,
            "persona": persona,
            "opening_scenario": opening_scenario
        }

    def create_simulation(self, user_vibe: UserVibe, persona_data: Dict[str, Any]) -> str:
        """
        Legacy method for backwards compatibility.
        """
        client = supabase_service.get_client()
        if not client:
            raise RuntimeError("Supabase client is not available.")

        sim_response = client.table("simulations").insert({
            "user_vibe": user_vibe.model_dump(),
            "status": "ACTIVE",
            "is_calibrated": True
        }).execute()
        
        if not sim_response.data:
            raise RuntimeError("Failed to create simulation row")
            
        simulation_id = sim_response.data[0]["id"]
        
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
        
        client.table("fluid_states").insert({
            "simulation_id": simulation_id,
            "emotional_bank_account": 0,
            "arousal_level": 0,
            "intellectual_boredom": 0,
            "current_craving": "Neutral"
        }).execute()
        
        memories = self.generate_backstory(persona_data)
        self.embed_and_store_memories(simulation_id, memories)
        
        return simulation_id

foundry_service = FoundryService()
