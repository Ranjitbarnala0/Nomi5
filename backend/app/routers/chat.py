from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.services.supabase import supabase_service
from backend.app.services.cortex import cortex_service
from backend.app.services.world import world_service

router = APIRouter()

class ChatRequest(BaseModel):
    simulation_id: str
    user_message: str

class ChatResponse(BaseModel):
    reply_text: Optional[str] = None
    narrative_bridge: Optional[str] = None
    director_log: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    The Main Loop:
    1. Checks Time (Time Skip)
    2. Checks Context (Schedule)
    3. Generates Reply (Director/Actor)
    4. Saves History
    """
    client = supabase_service.get_client()
    sim_id = request.simulation_id
    
    # 1. FETCH DATA (Persona, State, Last Interaction)
    # ---------------------------------------------------------
    # Fetch Persona
    p_data = client.table("persona_core").select("*").eq("simulation_id", sim_id).execute()
    if not p_data.data:
        raise HTTPException(status_code=404, detail="Simulation not found")
    persona = p_data.data[0]
    
    # Fetch Fluid State
    s_data = client.table("fluid_states").select("*").eq("simulation_id", sim_id).execute()
    fluid_state = s_data.data[0]
    
    # Fetch Last Interaction Time (from last message in memories)
    # We use the 'memories' table as the chat log for now
    last_msg_data = client.table("memories")\
        .select("created_at")\
        .eq("simulation_id", sim_id)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
        
    last_interaction = None
    if last_msg_data.data:
        # Parse Supabase timestamp format
        try:
            last_interaction = datetime.fromisoformat(last_msg_data.data[0]['created_at'].replace('Z', '+00:00'))
        except ValueError:
            last_interaction = datetime.now() # Fallback
    else:
        last_interaction = datetime.now()

    # 2. WORLD ENGINE (Time Skips & Schedule)
    # ---------------------------------------------------------
    current_time = datetime.now()
    narrative_text = None
    
    # Check for Time Skip
    time_skip_result = world_service.calculate_time_skip(last_interaction, current_time, persona)
    if time_skip_result:
        narrative_text = time_skip_result.get('narrative_text')
        # We save this narrative as a system message
        if narrative_text:
            client.table("memories").insert({
                "simulation_id": sim_id,
                "content": narrative_text,
                "memory_type": "NARRATIVE",
                "embedding": None 
            }).execute()
        
    # Get Schedule Context (Where is she right now?)
    schedule = world_service.get_schedule_state(current_time, persona)
    # Inject schedule into fluid state temporarily for the Director
    fluid_state['current_context'] = f"{schedule['activity']} at {schedule['location']}"
    
    # 3. PREPARE CORTEX INPUTS
    # ---------------------------------------------------------
    # Fetch Chat History (Last 10 lines) for Context
    history_data = client.table("memories")\
        .select("content")\
        .eq("simulation_id", sim_id)\
        .in_("memory_type", ["CHAT_HISTORY", "NARRATIVE"])\
        .order("created_at", desc=True)\
        .limit(10)\
        .execute()
    
    # Reverse to chronological order
    chat_history = [row['content'] for row in history_data.data][::-1] if history_data.data else []
    
    # Fetch "Recent Memories" (Vector search placeholder - for now just last 3 summary memories)
    # Note: Full vector search comes in Prompt 15.
    mem_data = client.table("memories")\
        .select("content")\
        .eq("simulation_id", sim_id)\
        .eq("memory_type", "CORE")\
        .limit(3)\
        .execute()
    recent_memories = [row['content'] for row in mem_data.data] if mem_data.data else []

    # 4. RUN CORTEX (Director -> Actor)
    # ---------------------------------------------------------
    cortex_result = cortex_service.process_chat(
        simulation_id=sim_id,
        user_input=request.user_message,
        persona=persona,
        fluid_state=fluid_state,
        recent_memories=recent_memories,
        chat_history=chat_history
    )
    
    # 5. PERSISTENCE
    # ---------------------------------------------------------
    # Save User Message
    client.table("memories").insert({
        "simulation_id": sim_id,
        "content": f"User: {request.user_message}",
        "memory_type": "CHAT_HISTORY"
    }).execute()
    
    # Save AI Reply
    if cortex_result.get('reply_text'):
        client.table("memories").insert({
            "simulation_id": sim_id,
            "content": f"{persona.get('name', 'Nomi')}: {cortex_result['reply_text']}",
            "memory_type": "CHAT_HISTORY"
        }).execute()

    return ChatResponse(
        reply_text=cortex_result.get('reply_text'),
        narrative_bridge=narrative_text,
        director_log=cortex_result.get('director_log'),
        new_state=cortex_result.get('new_state')
    )
