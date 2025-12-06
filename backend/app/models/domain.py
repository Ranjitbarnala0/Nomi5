from pydantic import BaseModel, Field
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime

class UserVibe(BaseModel):
    openness: float
    neuroticism: float
    aggression: float
    intellect_priority: float
    materialism: float
    detected_archetype: str
    match_strategy: str

class PersonaCoreBase(BaseModel):
    name: str
    appearance: str
    voice_texture: str
    core_wound: str
    defense_mechanism: str
    attachment_style: str
    values_matrix: Dict[str, int]
    sexual_orientation: str

class FluidStateBase(BaseModel):
    emotional_bank_account: int = Field(default=0, ge=-100, le=100)
    current_craving: Optional[str] = None
    arousal_level: int = Field(default=0, ge=0, le=100)
    intellectual_boredom: int = Field(default=0, ge=0, le=100)

class SimulationCreate(BaseModel):
    user_vibe: UserVibe

class DirectorOutput(BaseModel):
    internal_monologue: str
    emotional_reaction: str # e.g., "Annoyed", "Intrigued", "Scared"
    strategy: str # e.g., "Deflect", "Engage", "Test him"
    actor_instruction: str # The specific direction for the dialogue generator
