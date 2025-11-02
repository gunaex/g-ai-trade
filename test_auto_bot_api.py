"""
Quick API test for Auto Bot endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_config():
    """Test creating a bot config"""
    url = f"{BASE_URL}/api/auto-bot/create"
    payload = {
        "name": "Test Auto Bot",
        "symbol": "BTC/USDT",
        "budget": 5000,
        "risk_level": "moderate",
        "min_confidence": 0.75
    }
    
    print("\n1. Testing POST /api/auto-bot/create")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.json().get('config_id')
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def test_get_config(config_id):
    """Test getting bot config"""
    url = f"{BASE_URL}/api/auto-bot/config/{config_id}"
    
    print(f"\n2. Testing GET /api/auto-bot/config/{config_id}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_status():
    """Test getting bot status"""
    url = f"{BASE_URL}/api/auto-bot/status"
    
    print(f"\n3. Testing GET /api/auto-bot/status")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Running: {data.get('is_running')}")
        print(f"   AI Modules: {data.get('ai_modules')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_performance():
    """Test getting bot performance"""
    url = f"{BASE_URL}/api/auto-bot/performance"
    
    print(f"\n4. Testing GET /api/auto-bot/performance")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("AUTO BOT API TEST")
    print("=" * 60)
    print("\n⚠️  Make sure the server is running: uvicorn app.main:app --reload")
    
    # Test create config
    config_id = test_create_config()
    
    if config_id:
        # Test get config
        test_get_config(config_id)
    
    # Test status
    test_status()
    
    # Test performance
    test_performance()
    
    print("\n" + "=" * 60)
    print("✅ API tests completed!")
    print("=" * 60)
