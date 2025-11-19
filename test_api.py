#!/usr/bin/env python3
"""
Test script to verify API endpoints
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(path, description):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {description} - {path} ({response.status_code})")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ {description} - {path} (Error: {str(e)})")
        return False

def main():
    print("Testing API endpoints...\n")
    
    tests = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/docs", "API documentation"),
        ("/admin", "Admin API"),
        ("/user", "User API"),
    ]
    
    passed = 0
    total = len(tests)
    
    for path, desc in tests:
        if test_endpoint(path, desc):
            passed += 1
        print()
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All endpoints are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some endpoints are not working")
        sys.exit(1)

if __name__ == "__main__":
    main()