#!/usr/bin/env python3
"""
Run the FastAPI server with auto-detection
"""
import os
import sys
import uvicorn

# Add paths
sys.path.insert(0, '.')
sys.path.insert(0, './backend')

# Try to import and run the app
try:
    from main import app
    print("✓ Successfully imported app from main.py")
except ImportError:
    try:
        from backend.main import app
        print("✓ Successfully imported app from backend.main")
    except ImportError as e:
        print(f"✗ Failed to import FastAPI app: {e}")
        sys.exit(1)

# Run the server
print("Starting uvicorn server...")
uvicorn.run(app, host="0.0.0.0", port=8000)