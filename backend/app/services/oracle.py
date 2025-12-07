import json
import re
from typing import Dict, Any, Optional
from backend.app.services.openrouter import openrouter_service
from backend.app.services.supabase import supabase_service

# Calibration scenarios for the System to ask
CALIBRATION_SCENARIOS = [
    "You find a wallet on the ground with $500 cash and an ID. What do you do?",
    "A friend asks you to lie to their partner about where they were last night. How do you respond?",
    "You're in an elevator that stops between floors. A stranger next to you starts crying. What do you do?"
]

class OracleService:
    """
    The System - A neutral calibration interface that interviews users
    to build their psychological profile before generating a matched persona.
    """
    
    def get_system_message(self, step: int, user_profile: Dict[str, Any]) -> str:
        """
        Returns the appropriate System message based on calibration step.
        """
        if step == 0:
            return """[SYSTEM INITIALIZING...]

I am The System. I will calibrate your reality.

Before we begin, I need to know who you are.

Tell me: What is your name, age, and gender?
(Example: "Alex, 28, Male")"""

        elif step == 1:
            name = user_profile.get('name', 'User')
            return f"""Acknowledged, {name}. Calibration initiated.

SCENARIO 1:
{CALIBRATION_SCENARIOS[0]}

What do you do?"""

        elif step == 2:
            return f"""Noted. Processing response...

SCENARIO 2:
{CALIBRATION_SCENARIOS[1]}

How do you respond?"""

        elif step == 3:
            return f"""Interesting. Analyzing pattern...

SCENARIO 3 (Final):
{CALIBRATION_SCENARIOS[2]}

What do you do?"""

        else:
            return "[SYSTEM] Calibration complete. Generating your reality..."

    def parse_user_basics(self, user_input: str) -> Dict[str, Any]:
        """
        Parses name, age, gender from user input like "Alex, 28, Male"
        """
        prompt = f"""
        Extract the following from this user input: "{user_input}"
        
        Return JSON only:
        {{"name": "string", "age": int, "gender": "string"}}
        
        If any field is missing, use reasonable defaults.
        """
        
        raw = openrouter_service.generate_text(prompt, temperature=0.1)
        clean = re.sub(r"```json|```", "", raw).strip()
        
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Fallback parsing
            parts = user_input.replace(",", " ").split()
            return {
                "name": parts[0] if parts else "User",
                "age": 25,
                "gender": "Unknown"
            }

    def analyze_scenario_response(self, scenario: str, response: str) -> Dict[str, float]:
        """
        Analyzes a single scenario response for personality traits.
        """
        prompt = f"""
        SCENARIO: "{scenario}"
        USER RESPONSE: "{response}"
        
        Analyze for these traits (0.0 to 1.0):
        - empathy (caring about others)
        - assertiveness (taking action, being bold)
        - honesty (truth-telling tendency)
        - creativity (unconventional solutions)
        - anxiety (worry, hesitation)
        
        Return JSON only:
        {{"empathy": float, "assertiveness": float, "honesty": float, "creativity": float, "anxiety": float}}
        """
        
        raw = openrouter_service.generate_text(prompt, temperature=0.2)
        clean = re.sub(r"```json|```", "", raw).strip()
        
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"empathy": 0.5, "assertiveness": 0.5, "honesty": 0.5, "creativity": 0.5, "anxiety": 0.5}

    def process_calibration_step(
        self, 
        simulation_id: str, 
        user_input: str, 
        current_step: int,
        current_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processes a single step of calibration and returns the next System message.
        """
        client = supabase_service.get_client()
        updated_profile = current_profile.copy()
        
        if current_step == 0:
            # Parse name/age/gender
            basics = self.parse_user_basics(user_input)
            updated_profile.update(basics)
            updated_profile['scenario_responses'] = []
            
        elif current_step in [1, 2, 3]:
            # Analyze scenario response
            scenario_idx = current_step - 1
            analysis = self.analyze_scenario_response(
                CALIBRATION_SCENARIOS[scenario_idx], 
                user_input
            )
            
            if 'scenario_responses' not in updated_profile:
                updated_profile['scenario_responses'] = []
            
            updated_profile['scenario_responses'].append({
                'scenario': CALIBRATION_SCENARIOS[scenario_idx],
                'response': user_input,
                'analysis': analysis
            })
        
        # Move to next step
        next_step = current_step + 1
        is_complete = next_step > 3
        
        # Update database
        client.table("simulations").update({
            "user_profile": updated_profile,
            "calibration_step": next_step,
            "is_calibrated": is_complete
        }).eq("id", simulation_id).execute()
        
        # Get next message
        next_message = self.get_system_message(next_step, updated_profile)
        
        return {
            "system_reply": next_message,
            "is_calibrated": is_complete,
            "calibration_step": next_step,
            "user_profile": updated_profile
        }

    def calculate_final_profile(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates the final psychometric profile from all scenario responses.
        """
        responses = user_profile.get('scenario_responses', [])
        
        if not responses:
            return {
                "openness": 0.5,
                "neuroticism": 0.5,
                "aggression": 0.2,
                "intellect_priority": 0.5,
                "materialism": 0.3,
                "detected_archetype": "The Balanced",
                "match_strategy": "COMPLEMENTARY"
            }
        
        # Average the traits across all responses
        avg_empathy = sum(r['analysis'].get('empathy', 0.5) for r in responses) / len(responses)
        avg_assertiveness = sum(r['analysis'].get('assertiveness', 0.5) for r in responses) / len(responses)
        avg_honesty = sum(r['analysis'].get('honesty', 0.5) for r in responses) / len(responses)
        avg_creativity = sum(r['analysis'].get('creativity', 0.5) for r in responses) / len(responses)
        avg_anxiety = sum(r['analysis'].get('anxiety', 0.5) for r in responses) / len(responses)
        
        # Map to our standard profile format
        return {
            "openness": avg_creativity,
            "neuroticism": avg_anxiety,
            "aggression": 1.0 - avg_empathy,
            "intellect_priority": avg_creativity,
            "materialism": 1.0 - avg_honesty,
            "detected_archetype": self._determine_archetype(avg_empathy, avg_assertiveness, avg_creativity),
            "match_strategy": "COMPLEMENTARY" if avg_assertiveness < 0.5 else "CHALLENGE"
        }

    def _determine_archetype(self, empathy: float, assertiveness: float, creativity: float) -> str:
        """Determines user archetype based on trait averages."""
        if empathy > 0.7:
            return "The Caregiver"
        elif assertiveness > 0.7:
            return "The Leader"
        elif creativity > 0.7:
            return "The Artist"
        elif empathy < 0.3 and assertiveness > 0.5:
            return "The Rebel"
        else:
            return "The Observer"

    # Legacy methods for backwards compatibility
    def generate_liminal_scene(self) -> str:
        """Legacy: Generates an initial scene. Now returns System init message."""
        return self.get_system_message(0, {})

    def analyze_reaction(self, scenario: str, user_reaction: str) -> Dict[str, Any]:
        """Legacy: Analyze single reaction."""
        analysis = self.analyze_scenario_response(scenario, user_reaction)
        return {
            "user_vibe": {
                "openness": analysis.get('creativity', 0.5),
                "neuroticism": analysis.get('anxiety', 0.5),
                "aggression": 1.0 - analysis.get('empathy', 0.5),
                "intellect_priority": analysis.get('creativity', 0.5),
                "materialism": 0.3,
                "detected_archetype": "The Observer",
                "match_strategy": "COMPLEMENTARY"
            }
        }

oracle_service = OracleService()
