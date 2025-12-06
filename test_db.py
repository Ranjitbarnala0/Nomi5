from backend.app.services.supabase import supabase_service
print(f"Supabase connected: {supabase_service.get_client() is not None}")
