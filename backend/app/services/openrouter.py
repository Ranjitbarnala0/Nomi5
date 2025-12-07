import httpx
from typing import List
from backend.app.core.config import settings

class OpenRouterService:
    """
    AI Service using OpenRouter with NVIDIA Nemotron model.
    Primary AI provider for Project Nomi.
    """
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "nvidia/nemotron-nano-12b-v2-vl:free"
    
    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Generates text using OpenRouter with NVIDIA Nemotron model.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://project-nomi.app",
                "X-Title": "Project Nomi"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    return "[Error: No content returned from OpenRouter API]"
                    
        except Exception as e:
            error_msg = f"OpenRouter API Error: {str(e)}"
            print(error_msg)
            return "[System Error: AI generation failed]"
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generates text embeddings using OpenRouter.
        Used for memory storage and retrieval.
        Note: Uses a simple embedding approach since OpenRouter doesn't have a dedicated embedding endpoint.
        For production, consider using a dedicated embedding service.
        """
        try:
            # OpenRouter doesn't have a dedicated embedding endpoint
            # We'll use a simple hash-based embedding as a fallback
            # For production, you should integrate a proper embedding service
            import hashlib
            
            # Create a deterministic 768-dimension vector from text
            hash_bytes = hashlib.sha256(text.encode()).digest()
            # Expand to 768 dimensions by repeating and varying
            embedding = []
            for i in range(768):
                byte_val = hash_bytes[i % 32]
                # Normalize to [-1, 1] range with some variation
                val = ((byte_val + i) % 256) / 255.0 * 2 - 1
                embedding.append(val)
            
            return embedding
                    
        except Exception as e:
            print(f"OpenRouter Embedding Error: {e}")
            # Return a zero vector as fallback (768 dimensions)
            return [0.0] * 768

# Singleton instance
openrouter_service = OpenRouterService()
