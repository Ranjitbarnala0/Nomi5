
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from backend.app.services.supabase import supabase_service
from backend.app.services.nvidia import nvidia_service

router = APIRouter()

class SystemConfig(BaseModel):
    app_name: str
    version: str
    maintenance_mode: bool
    min_client_version: str
    features: Dict[str, bool]

class HealthStatus(BaseModel):
    database: str
    ai_engine: str
    vector_store: str

@router.get("/config", response_model=SystemConfig)
async def get_system_config():
    """
    The First Call: The Mobile App hits this on launch.
    Allows remote configuration of the client.
    """
    return SystemConfig(
        app_name="Project Nomi",
        version="1.0.0",
        maintenance_mode=False, # Set to True to lock the app remotely
        min_client_version="1.0.0", # Force users to update
        features={
            "voice_chat": False, # Feature flag to toggle future features
            "images": False,
            "nsfw_filter_override": True
        }
    )

@router.get("/diagnostics", response_model=HealthStatus)
async def run_diagnostics():
    """
    Deep Health Check: Verifies connections to Supabase and Nvidia AI.
    """
    # 1. Check Database
    try:
        supabase_service.get_client().table("simulations").select("count", count="exact").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # 2. Check AI Engine (Nvidia)
    try:
        # Simple generation check
        nvidia_service.generate_text("test", max_tokens=1)
        ai_status = "operational"
    except Exception as e:
        ai_status = f"error: {str(e)}"

    return HealthStatus(
        database=db_status,
        ai_engine=ai_status,
        vector_store="ready" if db_status == "connected" else "unavailable"
    )
