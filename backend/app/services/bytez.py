import httpx
from typing import List, Dict, Any

class BytezService:
    """
    Unified AI Service using Bytez API with Claude Sonnet 4.5
    Replaces NVIDIA and Gemini integrations.
    """
    
    def __init__(self):
        # Bytez API Key - will be loaded from environment
        from backend.app.core.config import settings
        self.api_key = settings.BYTEZ_API_KEY
        self.model = "anthropic/claude-sonnet-4-5"
        # Correct Bytez API endpoint
        self.base_url = "https://api.bytez.com/models/v2/openai/v1"
    
    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Generates text using Bytez API with Claude Sonnet 4.5.
        Compatible interface with the old nvidia_service.
        """
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
                elif 'output' in data:
                    return data['output']
                else:
                    return "[Error: No content returned from Bytez API]"
                    
        except Exception as e:
            error_msg = f"Bytez API Error: {str(e)}"
            print(error_msg)
            return "[System Error: AI generation failed]"
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generates text embeddings using Bytez API.
        Used for memory storage and retrieval.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "text-embedding-3-small",  # Use OpenAI-compatible embedding model
            "input": text,
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    return data['data'][0]['embedding']
                else:
                    raise ValueError("No embedding returned")
                    
        except Exception as e:
            print(f"Bytez Embedding Error: {e}")
            # Return a zero vector as fallback (768 dimensions typical)
            return [0.0] * 768

# Singleton instance
bytez_service = BytezService()
