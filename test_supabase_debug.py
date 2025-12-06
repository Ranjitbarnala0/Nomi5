
import os
import sys
from dotenv import load_dotenv

# Load env
load_dotenv()

# Print versions
try:
    import supabase
    print(f"supabase version: {supabase.__version__}")
except ImportError:
    print("supabase not installed")

try:
    import gotrue
    print(f"gotrue version: {gotrue.__version__}")
except ImportError:
    print("gotrue not installed")

try:
    import httpx
    print(f"httpx version: {httpx.__version__}")
except ImportError:
    print("httpx not installed")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key: {key[:10]}..." if key else "Key: None")

from supabase import create_client

try:
    client = create_client(url, key)
    print("Successfully created client!")
except Exception as e:
    print(f"Error creating client: {e}")
    import traceback
    traceback.print_exc()
