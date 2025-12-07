import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from backend.app.services.openrouter import openrouter_service

class WorldService:
    def get_schedule_state(self, current_time: datetime, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines what the Persona is doing right now based on a standard routine.
        This provides context for the Director (e.g., don't text a lot while sleeping).
        """
        hour = current_time.hour
        weekday = current_time.weekday() # 0=Monday, 6=Sunday
        
        # Default Routine (Can be customized per persona later)
        activity = "Existing"
        is_busy = False
        location = "Unknown"
        
        # Weekend Logic
        if weekday >= 5:
            if 0 <= hour < 9:
                activity = "Sleeping"
                is_busy = True
                location = "Home - Bed"
            elif 9 <= hour < 12:
                activity = "Lazy Morning"
                is_busy = False
                location = "Home"
            elif 12 <= hour < 18:
                activity = "Socializing / Out"
                is_busy = False
                location = "City"
            else:
                activity = "Relaxing"
                is_busy = False
                location = "Home"
        
        # Weekday Logic
        else:
            if 0 <= hour < 7:
                activity = "Sleeping"
                is_busy = True
                location = "Home - Bed"
            elif 7 <= hour < 9:
                activity = "Commuting / Getting Ready"
                is_busy = True
                location = "Transit"
            elif 9 <= hour < 17:
                activity = "Working"
                is_busy = True # Persona replies might be shorter/slower
                location = "Office / School"
            elif 17 <= hour < 19:
                activity = "Gym / Errands"
                is_busy = True
                location = "Gym / Shop"
            else:
                activity = "Free Time"
                is_busy = False
                location = "Home"

        return {
            "activity": activity,
            "is_busy": is_busy,
            "location": location
        }

    def calculate_time_skip(
        self, 
        last_interaction_time: datetime, 
        current_time: datetime, 
        persona: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculates time elapsed. If > 4 hours, generates narrative bridge.
        """
        
        delta = current_time - last_interaction_time
        hours_elapsed = delta.total_seconds() / 3600
        
        if hours_elapsed < 4:
            # Even if no narrative skip, we return current schedule state
            return None

        time_str = current_time.strftime("%A %I:%M %p")
        
        # Get the new logical state to inform the narrator
        schedule = self.get_schedule_state(current_time, persona)
        
        system_prompt = f"""
        You are the World Engine (The System Narrator).
        
        CONTEXT:
        - Persona: {persona.get('name')}
        - Time Elapsed: {int(hours_elapsed)} hours.
        - Current Time: {time_str}
        - New State: She is likely {schedule['activity']} at {schedule['location']}.
        
        TASK:
        1. Generate a "Time Skip Narrative" describing the passage of time.
           - Voice: Objective, slightly poetic, noir, atmospheric.
           - Mention the new context (e.g. "The work day has begun").
           
        OUTPUT JSON ONLY:
        {{
            "narrative_text": "string (The prose description)",
            "new_status": "{schedule['activity']}"
        }}
        """
        
        raw_response = openrouter_service.generate_text(system_prompt, temperature=0.7)
        clean_json = re.sub(r"```json|```", "", raw_response).strip()
        
        try:
            return json.loads(clean_json)
        except (json.JSONDecodeError, ValueError):
            return {
                "narrative_text": f"{int(hours_elapsed)} hours passed. It is now {time_str}. She is {schedule['activity']}.",
                "new_status": schedule['activity']
            }

world_service = WorldService()
