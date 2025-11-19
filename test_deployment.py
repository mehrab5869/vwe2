#!/usr/bin/env python3
"""
Test deployment scenarios to ensure uvicorn can find the ASGI app
"""
import os
import sys
import subprocess
import tempfile
import shutil

def test_entrypoint(entry_point):
    """Test if uvicorn can find the app with the given entry point"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "uvicorn", entry_point, "--host", "0.0.0.0", "--port", "8000"],
            capture_output=True,
            text=True,
            timeout=5  # Short timeout to just check if it starts
        )
        if "Application startup complete" in result.stdout or "Uvicorn running on" in result.stdout:
            print(f"✓ {entry_point} - SUCCESS")
            return True
        else:
            print(f"✗ {entry_point} - FAILED")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        # Timeout is good - means it started successfully
        print(f"✓ {entry_point} - SUCCESS (started)")
        return True
    except Exception as e:
        print(f"✗ {entry_point} - ERROR: {e}")
        return False

def main():
    # Set up paths like in container
    sys.path.insert(0, '.')
    sys.path.insert(0, './backend')
    
    print("Testing uvicorn entry points...\n")
    
    # Test different entry points
    entry_points = [
        "main:app",
        "backend.main:app",
        "app.main:app",
    ]
    
    results = []
    for ep in entry_points:
        results.append((ep, test_entrypoint(ep)))
    
    print("\n" + "="*50)
    print("Summary:")
    for ep, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {ep}")
    
    # Try to import directly
    print("\n" + "="*50)
    print("Direct import test:")
    try:
        from main import app
        print("✓ main:app - Direct import successful")
    except ImportError as e:
        print(f"✗ main:app - Direct import failed: {e}")
    
    try:
        from backend.main import app
        print("✓ backend.main:app - Direct import successful")
    except ImportError as e:
        print(f"✗ backend.main:app - Direct import failed: {e}")

if __name__ == "__main__":
    main()