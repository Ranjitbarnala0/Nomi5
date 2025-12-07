
import json
import re
from typing import Dict, List, Any, Optional
from backend.app.services.openrouter import openrouter_service
from backend.app.services.supabase import supabase_service
from backend.app.models.domain import DirectorOutput

class CortexService:
    def check_relationship_health(self, simulation_id: str, fluid_state: Dict[str, Any]) -> Optional[str]:
        """
        Gatekeeper: Checks if the relationship is healthy enough to continue.
        """
        trust = fluid_state.get('emotional_bank_account', 0)
        boredom = fluid_state.get('intellectual_boredom', 0)
        client = supabase_service.get_client()

        # 1. PERMADEATH
        if trust <= -100:
            client.table("simulations").update({"status": "BROKEN"}).eq("id", simulation_id).execute()
            return "[SYSTEM] This contact has blocked you. The connection is severed."

        # 2. GHOSTING
        if boredom > 80:
            return "[SYSTEM] Read 2 hours ago."

        return None

    def director_analysis(
        self, 
        user_input: str, 
        persona: Dict[str, Any], 
        fluid_state: Dict[str, Any], 
        recent_memories: List[str]
    ) -> DirectorOutput:
        """
        The Director Agent: Analyzes input and enforces Intimacy Gating.
        """
        trust = fluid_state.get('emotional_bank_account', 0)
        
        # INTIMACY THRESHOLD logic
        # 50 = "Intimate/Close"
        intimacy_logic = f"""
        RELATIONSHIP RULES:
        1. Current Trust Score: {trust}/100.
        2. IF User makes a Sexual/Romantic advance AND Trust < 50:
           - REACTION: Disgust or Coldness.
           - STRATEGY: Reject hard. Say "Ew" or "Stop" or "We aren't there yet".
        3. IF User makes a Sexual/Romantic advance AND Trust >= 50:
           - REACTION: Reciprocal/Flirty.
           - STRATEGY: Lean into it.
        """

        memory_context = "\n".join([f"- {m}" for m in recent_memories]) if recent_memories else "No recent memories."

        system_prompt = f"""
        You are the DIRECTOR for the persona "{persona.get('name', 'Nomi')}".
        
        PERSONA CORE:
        - Core Wound: {persona.get('core_wound')}
        - Defense Mechanism: {persona.get('defense_mechanism')}
        - Values: {json.dumps(persona.get('values_matrix'))}

        CURRENT STATE:
        - Trust: {trust} / 100
        - Context: {fluid_state.get('current_context', 'Unknown')}

        {intimacy_logic}

        RECENT CONTEXT:
        {memory_context}

        INPUT ANALYSIS:
        User said: "{user_input}"
        
        TASK:
        Analyze the input. Is it a normal chat, a conflict, or a romantic advance?
        Determine the Strategy based on the Trust Score.

        OUTPUT JSON ONLY:
        {{
            "internal_monologue": "string (Your raw thoughts)",
            "emotional_reaction": "string (e.g. Aroused, Disgusted, Warm, Neutral)",
            "strategy": "string (e.g. Flirt back, Hard Reject, Banter)",
            "actor_instruction": "string (Specific direction for the actor)"
        }}
        """

        raw_response = openrouter_service.generate_text(system_prompt, temperature=0.4)
        clean_json = re.sub(r"```json|```", "", raw_response).strip()
        
        try:
            data = json.loads(clean_json)
            return DirectorOutput(**data)
        except (json.JSONDecodeError, ValueError):
            return DirectorOutput(
                internal_monologue="Processing error.",
                emotional_reaction="Neutral",
                strategy="Default",
                actor_instruction="Respond normally."
            )

    def actor_generation(
        self, 
        user_input: str, 
        director_output: DirectorOutput, 
        persona: Dict[str, Any], 
        chat_history: List[str]
    ) -> str:
        """
        The Actor Agent: Generates dialogue.
        """
        history_text = "\n".join(chat_history[-5:]) if chat_history else "No previous chat."

        system_prompt = f"""
        You are the ACTOR playing "{persona.get('name')}".
        
        CHARACTER VOICE:
        - Texture: {persona.get('voice_texture')}
        
        CONTEXT:
        User said: "{user_input}"
        Director Instruction: "{director_output.actor_instruction}"
        (Internal Thought: {director_output.internal_monologue})
        
        CHAT HISTORY:
        {history_text}
        
        TASK:
        Write the response. Keep it casual (IM style).
        If the Director said "Reject", be firm.
        If the Director said "Reciprocate", be affectionate.
        """
        return openrouter_service.generate_text(system_prompt, temperature=0.9)

    def update_fluid_state(
        self,
        simulation_id: str,
        director_output: DirectorOutput,
        current_state: Dict[str, Any],
        user_input: str
    ) -> Dict[str, Any]:
        """
        Updates emotional variables.
        """
        trust_delta = 0
        boredom_delta = 0
        
        reaction = director_output.emotional_reaction.lower()
        
        # Trust Logic
        if reaction in ["warm", "aroused", "love"]:
            trust_delta = 2
        elif reaction in ["annoyed", "skeptical", "disgusted"]:
            trust_delta = -5 # Rejection hurts trust significantly
        elif reaction in ["hostile", "angry"]:
            trust_delta = -10
            
        # Boredom Logic
        if len(user_input.split()) < 3 and reaction == "bored":
            boredom_delta = 5
        elif reaction in ["intrigued", "excited", "aroused"]:
            boredom_delta = -5

        new_trust = max(-100, min(100, current_state.get('emotional_bank_account', 0) + trust_delta))
        new_boredom = max(0, min(100, current_state.get('intellectual_boredom', 0) + boredom_delta))
        
        client = supabase_service.get_client()
        client.table("fluid_states").update({
            "emotional_bank_account": new_trust,
            "intellectual_boredom": new_boredom,
            "last_updated": "now()"
        }).eq("simulation_id", simulation_id).execute()
        
        return {
            "emotional_bank_account": new_trust,
            "intellectual_boredom": new_boredom
        }

    def process_chat(
        self, 
        simulation_id: str,
        user_input: str, 
        persona: Dict[str, Any], 
        fluid_state: Dict[str, Any], 
        recent_memories: List[str],
        chat_history: List[str]
    ) -> Dict[str, Any]:
        """
        Orchestrator: Check Health -> Director -> Actor -> State Manager
        """
        # 1. Gatekeeper Check
        block_reason = self.check_relationship_health(simulation_id, fluid_state)
        if block_reason:
            return {
                "reply_text": block_reason,
                "director_log": {"internal_monologue": "Connection blocked."},
                "new_state": fluid_state
            }

        # 2. Director Thinks (With Intimacy Check)
        director_result = self.director_analysis(user_input, persona, fluid_state, recent_memories)
        
        # 3. Actor Speaks
        actor_reply = self.actor_generation(user_input, director_result, persona, chat_history)
        
        # 4. State Updates
        new_state = self.update_fluid_state(simulation_id, director_result, fluid_state, user_input)
        
        return {
            "reply_text": actor_reply,
            "director_log": director_result.model_dump(),
            "new_state": new_state
        }

cortex_service = CortexService()
