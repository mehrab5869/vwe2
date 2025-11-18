"""
Integration test demonstrating key rotation under simulated 429s
"""
import asyncio
import httpx
import json
from uuid import uuid4


API_URL = "http://localhost:8000"


async def test_key_rotation_with_429():
    """
    Simulate scenario where provider returns 429,
    system should mark key unhealthy and try next key
    """
    print("Integration Test: Key Rotation with 429")
    print("=" * 50)
    
    # This is a demonstration script
    # In a real scenario, you would:
    # 1. Create a base route
    # 2. Add multiple API keys to a pool
    # 3. Make requests that trigger 429 responses
    # 4. Verify that keys are rotated and marked unhealthy
    
    print("Note: This test requires:")
    print("1. Running backend server")
    print("2. Configured routes and keys")
    print("3. Mock provider that returns 429")
    print("\nFor full integration test, use k6 or similar tool")
    
    # Example request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/v1/chat/completions",
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": "test"}]
                }
            )
            print(f"Response status: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_key_rotation_with_429())

