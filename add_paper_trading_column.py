"""
Database migration to add paper_trading column to bot_configs table

Run this script to update existing database:
    python add_paper_trading_column.py
"""

from app.db import SessionLocal, engine
from sqlalchemy import text

def add_paper_trading_column():
    """Add paper_trading column with default value TRUE (safe mode)"""
    
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='bot_configs' AND column_name='paper_trading';
        """))
        
        if result.fetchone():
            print("✅ Column 'paper_trading' already exists")
            return
        
        # Add the column with default TRUE (paper trading enabled by default for safety)
        print("Adding 'paper_trading' column to bot_configs table...")
        db.execute(text("""
            ALTER TABLE bot_configs 
            ADD COLUMN paper_trading BOOLEAN DEFAULT TRUE;
        """))
        
        # Update existing configs to paper trading mode (safety first!)
        db.execute(text("""
            UPDATE bot_configs 
            SET paper_trading = TRUE 
            WHERE paper_trading IS NULL;
        """))
        
        db.commit()
        print("✅ Successfully added paper_trading column")
        print("⚠️  All existing configs set to PAPER TRADING mode (safe default)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DATABASE MIGRATION: Add Paper Trading Support")
    print("="*60 + "\n")
    
    add_paper_trading_column()
    
    print("\n" + "="*60)
    print("Migration complete!")
    print("="*60)
