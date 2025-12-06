from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from backend.app.models.domain import UserVibe
from backend.app.services.foundry import foundry_service

router = APIRouter()

class GenesisRequest(BaseModel):
    user_vibe: UserVibe

class GenesisResponse(BaseModel):
    simulation_id: str
    persona: Dict[str, Any]

@router.post("/genesis", response_model=GenesisResponse)
async def genesis(request: GenesisRequest):
    """
    Triggers the Foundry logic.
    1. Generates a Persona based on UserVibe.
    2. Persists all data to Supabase.
    3. Returns the new Simulation ID and Persona details.
    """
    try:
        # Generate the Soul
        persona_data = foundry_service.generate_soul(request.user_vibe)
        
        # Persist to DB
        simulation_id = foundry_service.create_simulation(request.user_vibe, persona_data)
        
        return GenesisResponse(
            simulation_id=simulation_id,
            persona=persona_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
