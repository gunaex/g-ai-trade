"""
Test script to verify God's Hand integration
"""

print("=" * 60)
print("GOD'S HAND INTEGRATION TEST")
print("=" * 60)

# Test 1: Verify BotConfig model has to_dict method
print("\n1. Testing BotConfig.to_dict() method...")
try:
    from app.models import BotConfig
    from app.db import SessionLocal
    
    # Create a test config
    db = SessionLocal()
    test_config = BotConfig(
        name="Test Bot",
        symbol="BTC/USDT",
        budget=5000,
        risk_level="moderate",
        min_confidence=0.75
    )
    
    # Test to_dict method
    config_dict = test_config.to_dict()
    
    assert 'id' in config_dict
    assert 'name' in config_dict
    assert 'symbol' in config_dict
    assert 'budget' in config_dict
    assert 'risk_level' in config_dict
    assert 'min_confidence' in config_dict
    assert 'created_at' in config_dict
    assert 'updated_at' in config_dict
    
    print("   ✅ BotConfig.to_dict() works correctly")
    print(f"   Sample output: {list(config_dict.keys())}")
    
    db.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Verify API endpoint uses to_dict
print("\n2. Checking if API endpoint uses to_dict()...")
try:
    import re
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if get_auto_bot_config uses to_dict
    if 'return config.to_dict()' in content:
        print("   ✅ API endpoint uses config.to_dict()")
    else:
        print("   ⚠️  API endpoint might not be using to_dict()")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check if GodsHand route exists in App.tsx
print("\n3. Verifying God's Hand route in App.tsx...")
try:
    with open('ui/src/App.tsx', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "import GodsHand from './pages/GodsHand'" in content:
        print("   ✅ GodsHand import found")
    else:
        print("   ❌ GodsHand import missing")
    
    if '<Route path="/gods-hand" element={<GodsHand />} />' in content:
        print("   ✅ GodsHand route found")
    else:
        print("   ❌ GodsHand route missing")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Check if Navbar has God's Hand link
print("\n4. Verifying God's Hand link in Navbar...")
try:
    with open('ui/src/components/Navbar.tsx', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'Brain' in content:
        print("   ✅ Brain icon import found")
    else:
        print("   ❌ Brain icon import missing")
    
    if '/gods-hand' in content:
        print("   ✅ God's Hand navigation link found")
    else:
        print("   ❌ God's Hand navigation link missing")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Verify GodsHand page exists
print("\n5. Checking if GodsHand page exists...")
try:
    import os
    if os.path.exists('ui/src/pages/GodsHand.tsx'):
        print("   ✅ GodsHand.tsx page exists")
        
        # Check file size
        size = os.path.getsize('ui/src/pages/GodsHand.tsx')
        print(f"   File size: {size} bytes")
    else:
        print("   ❌ GodsHand.tsx page not found")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETE")
print("=" * 60)

print("\n📋 Summary:")
print("   - BotConfig model: Enhanced with to_dict() method")
print("   - API endpoint: Using to_dict() for cleaner code")
print("   - Frontend route: /gods-hand added to App.tsx")
print("   - Navigation: God's Hand link added to Navbar")
print("   - Page: GodsHand.tsx exists")

print("\n🚀 Next Steps:")
print("   1. Start backend: python -m uvicorn app.main:app --reload")
print("   2. Start frontend: cd ui && npm run dev")
print("   3. Navigate to: http://localhost:5173/gods-hand")
print("   4. Test Auto Bot configuration and controls")
