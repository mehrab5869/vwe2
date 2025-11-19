#!/usr/bin/env python3
"""
Test script to validate imports and locate the FastAPI app
"""
import sys
import os
import traceback

# Add current directory and backend to path
sys.path.insert(0, '.')
sys.path.insert(0, './backend')

print("Testing imports...")

# Test 1: Try importing backend.main
try:
    from backend.main import app
    print("✓ Successfully imported app from backend.main")
    print(f"  App type: {type(app)}")
except Exception as e:
    print(f"✗ Failed to import from backend.main: {e}")
    traceback.print_exc()

# Test 2: Try importing main (root)
try:
    from main import app
    print("✓ Successfully imported app from main")
    print(f"  App type: {type(app)}")
except Exception as e:
    print(f"✗ Failed to import from main: {e}")
    traceback.print_exc()

# Test 3: Try importing app.main
try:
    from app.main import app
    print("✓ Successfully imported app from app.main")
    print(f"  App type: {type(app)}")
except Exception as e:
    print(f"✗ Failed to import from app.main: {e}")
    traceback.print_exc()

# Test 4: Check if we can access the health endpoint
try:
    from backend.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    print(f"✓ Health check response: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"✗ Health check failed: {e}")
    traceback.print_exc()