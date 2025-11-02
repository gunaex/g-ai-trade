"""
Database Initialization Script
สร้าง tables ทั้งหมด
"""

from app.db import engine, Base
from app.models import Trade, GridBot, DCABot, AuditLog, BotConfig

def init_database():
    """สร้าง tables ทั้งหมด"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    
    print("\nCreating database tables...")
    print("Tables to create:")
    print("  - trades")
    print("  - grid_bots")
    print("  - dca_bots")
    print("  - audit_logs")
    print("  - bot_configs")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("\n✅ Database tables created successfully!")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\nCreated tables:")
        for table in tables:
            print(f"  ✓ {table}")
        
        print("\n" + "=" * 60)
        print("DATABASE READY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    init_database()
