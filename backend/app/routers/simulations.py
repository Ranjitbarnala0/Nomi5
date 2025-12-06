
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.app.services.supabase import supabase_service

router = APIRouter()

class SimulationStatus(BaseModel):
    id: str
    status: str # ACTIVE, BROKEN, ARCHIVED
    emotional_bank_account: int
    name: str
    avatar: str

class ResetRequest(BaseModel):
    simulation_id: str

@router.get("/list", response_model=List[SimulationStatus])
async def list_simulations():
    """
    Returns all simulations for the user (in a real app, filtering by user_id would happen here).
    """
    client = supabase_service.get_client()
    
    # Join simulations with persona_core and fluid_states
    # Note: Supabase-py syntax for joins can be tricky. We'll do distinct fetches for safety/speed in this MVP.
    
    sims = client.table("simulations").select("*").execute()
    results = []
    
    for sim in sims.data:
        # Fetch Persona Name
        p_data = client.table("persona_core").select("name, appearance").eq("simulation_id", sim['id']).execute()
        persona = p_data.data[0] if p_data.data else {"name": "Unknown", "appearance": ""}
        
        # Fetch State
        s_data = client.table("fluid_states").select("emotional_bank_account").eq("simulation_id", sim['id']).execute()
        state = s_data.data[0] if s_data.data else {"emotional_bank_account": 0}
        
        results.append(SimulationStatus(
            id=sim['id'],
            status=sim['status'],
            emotional_bank_account=state['emotional_bank_account'],
            name=persona['name'],
            avatar=persona['appearance'] or "" # Handle None
        ))
        
    return results

@router.post("/reset")
async def reset_timeline(request: ResetRequest):
    """
    The 'Time Machine' Feature.
    Wipes the relationship history but keeps the Persona's soul intact.
    Used when a user hits 'Permadeath' and wants to try again.
    """
    client = supabase_service.get_client()
    sim_id = request.simulation_id
    
    try:
        # 1. Reset Status to ACTIVE
        client.table("simulations").update({"status": "ACTIVE"}).eq("id", sim_id).execute()
        
        # 2. Reset Fluid State to Neutral
        client.table("fluid_states").update({
            "emotional_bank_account": 0,
            "intellectual_boredom": 0,
            "current_craving": "Neutral",
            "arousal_level": 0
        }).eq("simulation_id", sim_id).execute()
        
        # 3. Wipe Chat History (But keep CORE memories so she has a backstory)
        # Deleting rows where memory_type IS NOT 'CORE'
        client.table("memories").delete()\
            .eq("simulation_id", sim_id)\
            .neq("memory_type", "CORE")\
            .execute()
            
        return {"message": "Timeline reset successfully. She doesn't remember you."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
