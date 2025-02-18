from dotenv import load_dotenv
import os

load_dotenv()

# Try getting from .env first
DATABASE_URL = os.getenv("DATABASE_URL")

# Print debug info
print("Environment variables:")
print(f"DATABASE_URL from .env: {DATABASE_URL}")
print(f"DATABASE_URL from system: {os.environ.get('DATABASE_URL')}")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 