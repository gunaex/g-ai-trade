"""
Auto-run database migrations on application startup
This ensures the database schema is always up-to-date
"""

import logging
from sqlalchemy import text
from app.db import SessionLocal

logger = logging.getLogger(__name__)

def run_migrations():
    """Run all pending database migrations"""
    logger.info("Running database migrations...")
    
    try:
        add_paper_trading_column()
        logger.info("✅ All migrations completed successfully")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        # Don't raise - allow app to start even if migration fails
        # This prevents crashes if migration was already run

def add_paper_trading_column():
    """Add paper_trading column to bot_configs table if it doesn't exist"""
    
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='bot_configs' AND column_name='paper_trading';
        """))
        
        if result.fetchone():
            logger.info("✅ Column 'paper_trading' already exists - skipping")
            return
        
        logger.info("Adding 'paper_trading' column to bot_configs table...")
        
        # Add the column with default TRUE (paper trading enabled by default for safety)
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
        logger.info("✅ Successfully added paper_trading column")
        logger.info("⚠️  All existing configs set to PAPER TRADING mode (safe default)")
        
    except Exception as e:
        logger.error(f"Error in add_paper_trading_column: {e}")
        db.rollback()
        raise
    finally:
        db.close()
