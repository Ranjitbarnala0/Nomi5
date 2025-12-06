
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.routers import oracle, foundry, chat, simulations, system

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
    )

    # CORS: Allow ALL origins for mobile app compatibility
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # REGISTER ALL ROUTERS (The Full Brain)
    # 1. Oracle: The Test (Liminal Space)
    application.include_router(oracle.router, prefix=f"{settings.API_V1_STR}/oracle", tags=["oracle"])
    
    # 2. Foundry: The Creation (Persona & Soul)
    application.include_router(foundry.router, prefix=f"{settings.API_V1_STR}/foundry", tags=["foundry"])
    
    # 3. Chat: The Interaction (Director, Actor, Memory, Time)
    application.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
    
    # 4. Simulations: The Management (List, Reset, Status)
    application.include_router(simulations.router, prefix=f"{settings.API_V1_STR}/simulations", tags=["simulations"])
    
    # 5. System: The Config (Handshake, Health)
    application.include_router(system.router, prefix=f"{settings.API_V1_STR}/system", tags=["system"])

    return application

app = create_application()

@app.get("/")
async def root():
    """
    Server Heartbeat.
    """
    return {
        "system": "Project Nomi", 
        "status": "online", 
        "component": "The Cortex (Backend)",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
