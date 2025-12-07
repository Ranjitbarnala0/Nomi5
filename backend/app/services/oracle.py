import json
import re
from typing import Dict, Any
from backend.app.services.openrouter import openrouter_service

class OracleService:
    def generate_liminal_scene(self) -> str:
        """
        Generates a solitary, high-friction scenario to test the user.
        The scene represents a 'Liminal Space' managed by the System.
        """
        system_prompt = """
        You are the 'System' or 'Narrator' of a reality simulation.
        Your task is to generate a 'Liminal Scene' to test a new user.
        
        RULES:
        1. The setting must be solitary and high-friction (e.g., a rainy bus stop with no umbrella, a broken elevator, an empty art gallery with a loud noise).
        2. Do NOT spawn any other characters yet. The user is alone.
        3. Describe the sensory details: the cold, the dampness, the silence, or the noise.
        4. Length: Short. Max 3-4 sentences.
        5. Tone: Objective, slightly cold, noir, observant.
        6. CRITICAL: You MUST end the output with the exact phrase: "What do you do?"
        
        Generate the scene now.
        """
        return openrouter_service.generate_text(system_prompt, temperature=0.8)

    def analyze_reaction(self, scenario: str, user_reaction: str) -> Dict[str, Any]:
        """
        Analyzes the user's reaction to the liminal scene and extracts a psychometric profile.
        Returns a dictionary matching the UserVibe schema.
        """
        system_prompt = f"""
        You are a Psychometric Profiler Agent.
        Your goal is to analyze a user's behavior in a high-friction scenario and extract their psychological values.
        
        SCENARIO: "{scenario}"
        USER REACTION: "{user_reaction}"
        
        TASK:
        Analyze the reaction for the following traits (0.0 to 1.0 scale):
        - openness (Creative, curious vs. closed)
        - neuroticism (Anxious, volatile vs. stable)
        - aggression (Hostile vs. peaceful)
        - intellect_priority (Abstract thinking vs. physical action)
        - materialism (Concern for objects/status vs. internal state)
        
        Determine the 'detected_archetype' (e.g., The Observer, The Fighter, The Stoic, The Jester).
        Determine the 'match_strategy' (COMPLEMENTARY, MIRROR, or CHALLENGE).
        
        OUTPUT FORMAT:
        Return ONLY a raw JSON object. Do not include markdown formatting like ```json.
        
        Example JSON:
        {{
            "openness": 0.8,
            "neuroticism": 0.2,
            "aggression": 0.1,
            "intellect_priority": 0.9,
            "materialism": 0.1,
            "detected_archetype": "The Observer",
            "match_strategy": "COMPLEMENTARY"
        }}
        """
        
        raw_response = openrouter_service.generate_text(system_prompt, temperature=0.2)
        
        # Clean response if AI adds markdown code blocks
        clean_json = re.sub(r"```json|```", "", raw_response).strip()
        
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            # Fallback or error handling if JSON is malformed
            raise ValueError(f"Failed to parse psychometric profile: {raw_response}")

oracle_service = OracleService()
