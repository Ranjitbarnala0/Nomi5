
import requests
import json
from backend.app.core.config import settings

class NvidiaService:
    def __init__(self):
        # Using NVIDIA API Key from settings
        self.api_key = settings.NVIDIA_API_KEY
        self.model_name = "nvidia/nemotron-nano-12b-v2-vl"
        self.invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"

    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Generates text using the NVIDIA Nemotron model via standard HTTP requests.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # We use "/think" as the system prompt to encourage Chain-of-Thought (CoT) reasoning
        # which benefits this specific model (nemotron-nano).
        full_system_prompt = "/think"

        messages = [
            {
                "role": "system",
                "content": full_system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stream": False
        }

        try:
            response = requests.post(self.invoke_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                return content
            else:
                return "[Error: No content returned from NVIDIA API]"

        except Exception as e:
            error_msg = f"NVIDIA API Error: {str(e)}"
            if 'response' in locals():
                try:
                    error_msg += f" | Details: {response.text}"
                except:
                    pass
            print(error_msg)
            return "[System Error: AI generation failed]"

nvidia_service = NvidiaService()
