
from backend.app.services.gemini import gemini_service

try:
    print("Sending request to NVIDIA API...")
    response = gemini_service.generate_text("Hello, who are you?")
    print(f"Response received: {response}")
    if "Error" in response:
        print("Verification Failed.")
    else:
        print("Verification Successful.")
except Exception as e:
    print(f"Verification Crashed: {e}")
