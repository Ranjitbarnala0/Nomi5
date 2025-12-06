from backend.app.services.gemini import gemini_service
import asyncio

try:
    print("Testing Gemini Connection...")
    # Synchronous call as generate_text is synchronous in the service
    response = gemini_service.generate_text("Say 'System Online' and nothing else.", temperature=0.1)
    print(f"Response: {response}")
except Exception as e:
    print(f"FAILED: {e}")
