from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.oracle import oracle_service
from backend.app.models.domain import UserVibe

router = APIRouter()

class LiminalResponse(BaseModel):
    scenario_text: str

class AnalysisRequest(BaseModel):
    scenario: str
    user_reaction: str

class AnalysisResponse(BaseModel):
    user_vibe: UserVibe

@router.post("/init", response_model=LiminalResponse)
async def initialize_simulation():
    """
    Entry point for a new simulation.
    Generates the 'Liminal Scene' to test user behavior.
    """
    try:
        scenario = oracle_service.generate_liminal_scene()
        return LiminalResponse(scenario_text=scenario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_user(request: AnalysisRequest):
    """
    Step 2: Analyzes the user's reaction to the Liminal Scene.
    Returns the psychometric profile (UserVibe) needed to spawn the Nomi.
    """
    try:
        profile_data = oracle_service.analyze_reaction(request.scenario, request.user_reaction)
        # Validate against domain model
        user_vibe = UserVibe(**profile_data)
        return AnalysisResponse(user_vibe=user_vibe)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
