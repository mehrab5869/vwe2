#!/usr/bin/env python3
"""
Test script to verify all routes are working
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(path, description, expected_content=None):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {description} - {path} ({response.status_code})")
        
        if expected_content and response.status_code == 200:
            content_found = expected_content.lower() in response.text.lower()
            if content_found:
                print(f"   ✓ Contains expected content: {expected_content}")
            else:
                print(f"   ⚠ Missing expected content: {expected_content}")
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ {description} - {path} (Error: {str(e)})")
        return False

def main():
    print("Testing all routes...\n")
    
    tests = [
        ("/", "Root endpoint", "API Proxy Management"),
        ("/health", "Health check", "healthy"),
        ("/admin", "Admin Panel", "Admin Panel"),
        ("/user", "User Dashboard", "User Dashboard"),
        ("/docs", "API documentation", "swagger"),
        ("/admin/api/docs", "Admin API docs", "swagger"),
        ("/user/api/docs", "User API docs", "swagger"),
    ]
    
    passed = 0
    total = len(tests)
    
    for path, desc, expected in tests:
        if test_endpoint(path, desc, expected):
            passed += 1
        print()
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All routes are working correctly!")
        print("\nDeployment ready for Sliplane!")
        print("- Backend API: /api/*")
        print("- Admin UI: /admin")
        print("- User Dashboard: /user")
        sys.exit(0)
    else:
        print("\n❌ Some routes are not working")
        sys.exit(1)

if __name__ == "__main__":
    main()