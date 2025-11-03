"""
Test script for per-user API key management
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api_keys():
    print("=" * 60)
    print("Testing Per-User API Key Management")
    print("=" * 60)
    
    # 1. Login as admin
    print("\n1. Logging in as admin...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    login_data = login_response.json()
    access_token = login_data["access_token"]
    print(f"✅ Login successful! Token: {access_token[:20]}...")
    
    # Headers with auth token
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 2. Check initial API key status
    print("\n2. Checking API key status...")
    status_response = requests.get(f"{BASE_URL}/auth/api-keys/status", headers=headers)
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"✅ Has API keys: {status_data['has_api_keys']}")
        if status_data['api_key_preview']:
            print(f"   Preview: {status_data['api_key_preview']}")
    else:
        print(f"❌ Status check failed: {status_response.text}")
        return
    
    # 3. Save new API keys
    print("\n3. Saving test API keys...")
    save_response = requests.post(
        f"{BASE_URL}/auth/api-keys",
        headers=headers,
        json={
            "binance_api_key": "TEST_API_KEY_1234567890ABCDEF",
            "binance_api_secret": "TEST_SECRET_KEY_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        }
    )
    
    if save_response.status_code == 200:
        save_data = save_response.json()
        print(f"✅ {save_data['message']}")
        print(f"   Has keys: {save_data['has_api_keys']}")
    else:
        print(f"❌ Save failed: {save_response.text}")
        return
    
    # 4. Check status again to see preview
    print("\n4. Checking API key status after save...")
    status_response = requests.get(f"{BASE_URL}/auth/api-keys/status", headers=headers)
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"✅ Has API keys: {status_data['has_api_keys']}")
        print(f"   Preview: {status_data['api_key_preview']}")
    else:
        print(f"❌ Status check failed: {status_response.text}")
    
    # 5. Update API keys
    print("\n5. Updating API keys...")
    update_response = requests.post(
        f"{BASE_URL}/auth/api-keys",
        headers=headers,
        json={
            "binance_api_key": "UPDATED_KEY_9876543210FEDCBA",
            "binance_api_secret": "UPDATED_SECRET_ZYXWVUTSRQPONMLKJIHGFEDCBA"
        }
    )
    
    if update_response.status_code == 200:
        update_data = update_response.json()
        print(f"✅ {update_data['message']}")
    else:
        print(f"❌ Update failed: {update_response.text}")
    
    # 6. Check status after update
    print("\n6. Checking API key status after update...")
    status_response = requests.get(f"{BASE_URL}/auth/api-keys/status", headers=headers)
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"✅ Has API keys: {status_data['has_api_keys']}")
        print(f"   Preview: {status_data['api_key_preview']}")
    else:
        print(f"❌ Status check failed: {status_response.text}")
    
    # 7. Delete API keys
    print("\n7. Deleting API keys...")
    delete_response = requests.delete(f"{BASE_URL}/auth/api-keys", headers=headers)
    
    if delete_response.status_code == 200:
        delete_data = delete_response.json()
        print(f"✅ {delete_data['message']}")
    else:
        print(f"❌ Delete failed: {delete_response.text}")
    
    # 8. Check final status
    print("\n8. Checking API key status after delete...")
    status_response = requests.get(f"{BASE_URL}/auth/api-keys/status", headers=headers)
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"✅ Has API keys: {status_data['has_api_keys']}")
        print(f"   Preview: {status_data['api_key_preview']}")
    else:
        print(f"❌ Status check failed: {status_response.text}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_api_keys()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend at http://localhost:8000")
        print("   Make sure the backend is running: python app/main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
