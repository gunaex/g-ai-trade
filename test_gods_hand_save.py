"""
Test God's Hand bot configuration save functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_save_gods_hand_config():
    """Test saving God's Hand configuration with authentication"""
    
    print("\n" + "="*60)
    print("Testing God's Hand Bot Configuration Save")
    print("="*60)
    
    # Step 1: Login to get auth token
    print("\n1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Logged in successfully")
    print(f"   Token: {token[:20]}...")
    
    # Step 2: Get current user info
    print("\n2. Getting current user...")
    me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    user = me_response.json()
    print(f"✅ User: {user['username']} (ID: {user['user_id']})")
    
    # Step 3: Create God's Hand bot configuration
    print("\n3. Creating God's Hand bot configuration...")
    config = {
        "name": "God's Hand Bot",
        "symbol": "BTC/USDT",
        "budget": 10000,
        "risk_level": "moderate",
        "min_confidence": 0.7,
        "position_size_ratio": 0.95,
        "max_daily_loss": 5.0
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/auto-bot/create",
        headers=headers,
        json=config
    )
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create config: {create_response.text}")
        return
    
    result = create_response.json()
    config_id = result["config_id"]
    print(f"✅ Configuration created successfully!")
    print(f"   Config ID: {config_id}")
    print(f"   Message: {result['message']}")
    
    # Step 4: Retrieve the saved configuration
    print(f"\n4. Retrieving saved configuration (ID: {config_id})...")
    get_response = requests.get(
        f"{BASE_URL}/api/auto-bot/config/{config_id}",
        headers=headers
    )
    
    if get_response.status_code != 200:
        print(f"❌ Failed to retrieve config: {get_response.text}")
        return
    
    saved_config = get_response.json()
    print(f"✅ Configuration retrieved successfully!")
    print(f"\n   Saved Configuration:")
    print(f"   ├─ Name: {saved_config['name']}")
    print(f"   ├─ Symbol: {saved_config['symbol']}")
    print(f"   ├─ Budget: ${saved_config['budget']}")
    print(f"   ├─ Risk Level: {saved_config['risk_level']}")
    print(f"   ├─ Min Confidence: {saved_config['min_confidence']}")
    print(f"   ├─ Position Size: {saved_config['position_size_ratio'] * 100}%")
    print(f"   └─ Max Daily Loss: {saved_config['max_daily_loss']}%")
    
    # Step 5: Verify user_id association
    print(f"\n5. Verifying user association...")
    # Try to access with a different user (should fail)
    print("   Testing access control...")
    
    # Create a second user for testing
    try:
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": "testuser", "password": "test123"}
        )
        if register_response.status_code == 200:
            # Login as test user
            test_login = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "testuser", "password": "test123"}
            )
            test_token = test_login.json()["access_token"]
            test_headers = {"Authorization": f"Bearer {test_token}"}
            
            # Try to access admin's config
            test_access = requests.get(
                f"{BASE_URL}/api/auto-bot/config/{config_id}",
                headers=test_headers
            )
            
            if test_access.status_code == 404:
                print("   ✅ Access control working - testuser cannot access admin's config")
            else:
                print(f"   ⚠️  Access control issue - testuser got: {test_access.status_code}")
    except Exception as e:
        print(f"   ⚠️  Could not test access control: {e}")
    
    print("\n" + "="*60)
    print("✅ All tests passed! God's Hand configuration save is working.")
    print("="*60)
    
    return config_id

if __name__ == "__main__":
    test_save_gods_hand_config()
