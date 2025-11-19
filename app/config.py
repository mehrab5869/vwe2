import sys
import os
# Add backend and backend/app to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
backend_app_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')
if backend_app_path not in sys.path:
    sys.path.insert(0, backend_app_path)

# Import from backend.app.config with fallback
try:
    from backend.app.config import *
    # If DATABASE_URL is localhost, try to use environment variable or fallback to SQLite
    if 'DATABASE_URL' in locals() and 'localhost:5432' in DATABASE_URL:
        # Check if DATABASE_URL is provided in environment
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url and 'localhost' not in env_db_url:
            DATABASE_URL = env_db_url
            print(f"Using DATABASE_URL from environment: {env_db_url}")
        else:
            # Fallback to SQLite for development
            DATABASE_URL = "sqlite:///./app.db"
            print(f"Using SQLite fallback database: {DATABASE_URL}")
except ImportError as e:
    print(f"Could not import backend config: {e}")
    # Fallback settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "change-this-in-production-min-32-chars-required")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change-this-32-byte-key-in-production-use-32-chars")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))