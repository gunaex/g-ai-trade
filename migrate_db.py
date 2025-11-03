"""
Database migration script to add per-user API key columns
"""
import sqlite3
import os

DB_PATH = "g_ai_trade.db"

def migrate_database():
    print("=" * 60)
    print("Database Migration: Adding Per-User API Key Columns")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"\nExisting columns: {', '.join(columns)}")
        
        # Add binance_api_key column if not exists
        if 'binance_api_key' not in columns:
            print("\n➕ Adding 'binance_api_key' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN binance_api_key TEXT")
            print("✅ Column 'binance_api_key' added successfully")
        else:
            print("\n✓ Column 'binance_api_key' already exists")
        
        # Add binance_api_secret column if not exists
        if 'binance_api_secret' not in columns:
            print("➕ Adding 'binance_api_secret' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN binance_api_secret TEXT")
            print("✅ Column 'binance_api_secret' added successfully")
        else:
            print("✓ Column 'binance_api_secret' already exists")
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"\nUpdated columns: {', '.join(updated_columns)}")
        
        print("\n" + "=" * 60)
        print("✅ Database migration completed successfully!")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
