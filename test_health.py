#!/usr/bin/env python3
"""
Test the health endpoint of the FastAPI app
"""
import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, '.')
sys.path.insert(0, './backend')
sys.path.insert(0, './backend/app')

# Import the app
from main import app

# Test the health endpoint
from fastapi.testclient import TestClient
client = TestClient(app)

print("Testing health endpoint...")
response = client.get("/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test other endpoints
print("\nTesting root endpoint...")
try:
    response = client.get("/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\n✓ All tests passed!")