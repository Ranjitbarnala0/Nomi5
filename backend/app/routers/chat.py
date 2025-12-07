from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from backend.app.services.supabase import supabase_service
from backend.app.services.cortex import cortex_service
from backend.app.services.world import world_service
from backend.app.services.oracle import oracle_service
from backend.app.services.foundry import foundry_service

router = APIRouter()

class ChatRequest(BaseModel):
    simulation_id: str
    user_message: str

class ChatResponse(BaseModel):
    reply_text: Optional[str] = None
    narrative_bridge: Optional[str] = None
    director_log: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    is_calibrated: Optional[bool] = None
    persona_name: Optional[str] = None
    opening_scenario: Optional[str] = None

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    The Main Loop with 2-Phase Routing:
    
    PHASE 1 (Calibration):
    - If is_calibrated = False -> Route to Oracle (System Interview)
    - After calibration completes -> Generate Persona + Scenario
    
    PHASE 2 (Chat):
    - If is_calibrated = True -> Route to Cortex (Character AI)
    """
    try:
        client = supabase_service.get_client()
        sim_id = request.simulation_id
        
        # 1. FETCH SIMULATION STATE
        sim_data = client.table("simulations").select("*").eq("id", sim_id).execute()
        
        if not sim_data.data:
            raise HTTPException(status_code=404, detail="Simulation not found")
        
        simulation = sim_data.data[0]
        is_calibrated = simulation.get('is_calibrated', False)
        calibration_step = simulation.get('calibration_step', 0)
        user_profile = simulation.get('user_profile', {})
        
        # ========================================
        # PHASE 1: CALIBRATION MODE (The System)
        # ========================================
        if not is_calibrated:
            # Process calibration step
            result = oracle_service.process_calibration_step(
                simulation_id=sim_id,
                user_input=request.user_message,
                current_step=calibration_step,
                current_profile=user_profile
            )
            
            # Check if calibration just completed
            if result['is_calibrated']:
                # Generate the persona and opening scenario for THIS simulation
                genesis_result = foundry_service.genesis_for_simulation(
                    simulation_id=sim_id,
                    user_profile=result['user_profile']
                )
                
                # Update simulation with new data
                print(f"[CHAT] Updating simulation {sim_id} to calibrated")
                update_result = client.table("simulations").update({
                    "is_calibrated": True,
                    "status": "ACTIVE",
                    "opening_scenario": genesis_result['opening_scenario']
                }).eq("id", sim_id).execute()
                print(f"[CHAT] Update result: {update_result.data}")
                
                # Create the transition narrative
                persona_name = genesis_result['persona']['name']
                transition_text = f"""[CALIBRATION COMPLETE]

Profile analyzed. Match found.

Generating reality...

---

{genesis_result['opening_scenario']}"""
                
                return ChatResponse(
                    reply_text=transition_text,
                    is_calibrated=True,
                    persona_name=persona_name,
                    opening_scenario=genesis_result['opening_scenario']
                )
            else:
                # Still calibrating - return next System message
                return ChatResponse(
                    reply_text=result['system_reply'],
                    is_calibrated=False
                )
        
        # ========================================
        # PHASE 2: CHAT MODE (The Character)
        # ========================================
        else:
            # Fetch Persona
            p_data = client.table("persona_core").select("*").eq("simulation_id", sim_id).execute()
            if not p_data.data:
                raise HTTPException(status_code=404, detail="Persona not found for simulation")
            persona = p_data.data[0]
            
            # Fetch Fluid State
            s_data = client.table("fluid_states").select("*").eq("simulation_id", sim_id).execute()
            if not s_data.data:
                raise HTTPException(status_code=404, detail="Fluid state not found")
            fluid_state = s_data.data[0]
            
            # Fetch Last Interaction Time
            last_msg_data = client.table("memories")\
                .select("created_at")\
                .eq("simulation_id", sim_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
                
            last_interaction = None
            if last_msg_data.data:
                try:
                    last_interaction = datetime.fromisoformat(
                        last_msg_data.data[0]['created_at'].replace('Z', '+00:00')
                    )
                except ValueError:
                    last_interaction = datetime.now()
            else:
                last_interaction = datetime.now()

            # WORLD ENGINE (Time Skips & Schedule)
            current_time = datetime.now()
            narrative_text = None
            
            time_skip_result = world_service.calculate_time_skip(last_interaction, current_time, persona)
            if time_skip_result:
                narrative_text = time_skip_result.get('narrative_text')
                if narrative_text:
                    client.table("memories").insert({
                        "simulation_id": sim_id,
                        "content": narrative_text,
                        "memory_type": "NARRATIVE",
                        "embedding": None 
                    }).execute()
                
            # Get Schedule Context
            schedule = world_service.get_schedule_state(current_time, persona)
            fluid_state['current_context'] = f"{schedule['activity']} at {schedule['location']}"
            
            # PREPARE CORTEX INPUTS
            history_data = client.table("memories")\
                .select("content")\
                .eq("simulation_id", sim_id)\
                .in_("memory_type", ["CHAT_HISTORY", "NARRATIVE"])\
                .order("created_at", desc=True)\
                .limit(10)\
                .execute()
            
            chat_history = [row['content'] for row in history_data.data][::-1] if history_data.data else []
            
            mem_data = client.table("memories")\
                .select("content")\
                .eq("simulation_id", sim_id)\
                .eq("memory_type", "CORE")\
                .limit(3)\
                .execute()
            recent_memories = [row['content'] for row in mem_data.data] if mem_data.data else []

            # RUN CORTEX (Director -> Actor)
            cortex_result = cortex_service.process_chat(
                simulation_id=sim_id,
                user_input=request.user_message,
                persona=persona,
                fluid_state=fluid_state,
                recent_memories=recent_memories,
                chat_history=chat_history
            )
            
            # PERSISTENCE
            client.table("memories").insert({
                "simulation_id": sim_id,
                "content": f"User: {request.user_message}",
                "memory_type": "CHAT_HISTORY"
            }).execute()
            
            if cortex_result.get('reply_text'):
                client.table("memories").insert({
                    "simulation_id": sim_id,
                    "content": f"{persona.get('name', 'Character')}: {cortex_result['reply_text']}",
                    "memory_type": "CHAT_HISTORY"
                }).execute()

            return ChatResponse(
                reply_text=cortex_result.get('reply_text'),
                narrative_bridge=narrative_text,
                director_log=cortex_result.get('director_log'),
                new_state=cortex_result.get('new_state'),
                is_calibrated=True,
                persona_name=persona.get('name')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CHAT ERROR: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start", response_model=ChatResponse)
async def start_new_simulation():
    """
    Creates a new simulation in calibration mode and returns the first System message.
    """
    try:
        client = supabase_service.get_client()
        
        # Create new simulation in calibration mode
        sim_response = client.table("simulations").insert({
            "status": "CALIBRATING",
            "is_calibrated": False,
            "calibration_step": 0,
            "user_profile": {}
        }).execute()
        
        if not sim_response.data:
            raise HTTPException(status_code=500, detail="Failed to create simulation")
        
        simulation_id = sim_response.data[0]["id"]
        
        # Get the first System message
        first_message = oracle_service.get_system_message(0, {})
        
        return ChatResponse(
            reply_text=first_message,
            is_calibrated=False,
            new_state={"simulation_id": simulation_id}
        )
        
    except Exception as e:
        import traceback
        print(f"START ERROR: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
