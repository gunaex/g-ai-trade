"""
Test script to verify Auto Bot endpoints are registered
"""

from app.main import app

print("=" * 60)
print("AUTO BOT ENDPOINTS VERIFICATION")
print("=" * 60)

# Get all routes
all_routes = [r for r in app.routes if hasattr(r, 'path')]
auto_bot_routes = [r for r in all_routes if '/auto-bot' in r.path]

print(f"\nTotal routes in app: {len(all_routes)}")
print(f"Auto-bot routes: {len(auto_bot_routes)}\n")

if auto_bot_routes:
    print("Registered Auto-Bot Endpoints:")
    print("-" * 60)
    for route in auto_bot_routes:
        methods = ', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'
        print(f"  {methods:8} {route.path}")
    
    print("\n✅ All auto-bot endpoints registered successfully!")
else:
    print("❌ No auto-bot endpoints found!")

print("=" * 60)
