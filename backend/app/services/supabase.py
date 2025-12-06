from supabase import create_client, Client
from backend.app.core.config import settings

class SupabaseService:
    def __init__(self):
        self.url: str = settings.SUPABASE_URL
        self.key: str = settings.SUPABASE_KEY
        self.client: Client | None = None
        try:
            self.client = create_client(self.url, self.key)
        except Exception as e:
            print(f"Warning: Supabase client failed to initialize: {e}")

    def get_client(self) -> Client:
        if not self.client:
             # Try connecting again or raise error
            try:
                self.client = create_client(self.url, self.key)
            except Exception:
                raise RuntimeError("Supabase client is not initialized. Please check SUPABASE_URL and SUPABASE_KEY in .env")
        return self.client

# Singleton instance
supabase_service = SupabaseService()
