import sys
import os
# Add backend and backend/app to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
backend_app_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')
if backend_app_path not in sys.path:
    sys.path.insert(0, backend_app_path)

# Import from backend.app.encryption
from backend.app.encryption import *