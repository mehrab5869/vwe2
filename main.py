"""
API Proxy Management Platform - Main Application Entry Point
"""
import sys
import os
from pathlib import Path

# Add backend and backend/app to Python path
current_dir = Path(__file__).parent
backend_dir = current_dir / "backend"
app_dir = current_dir / "backend" / "app"

sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(app_dir))

# Now import the FastAPI app
try:
    from backend.main import app
except ImportError:
    # Fallback for different deployment scenarios
    import importlib
    spec = importlib.util.spec_from_file_location("backend_main", backend_dir / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["backend.main"] = module
    spec.loader.exec_module(module)
    app = module.app

# Export the FastAPI app instance
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)