from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
from app.db import Base

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # User-specific API credentials (encrypted)
    binance_api_key = Column(String, nullable=True)
    binance_api_secret = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert User to dictionary (exclude sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'has_api_keys': bool(self.binance_api_key and self.binance_api_secret),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)  # BUY or SELL
    amount = Column(Float)
    price = Column(Float, nullable=True)
    filled_price = Column(Float, nullable=True)
    status = Column(String, default="pending")
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class GridBot(Base):
    __tablename__ = "grid_bots"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    lower_price = Column(Float)
    upper_price = Column(Float)
    grid_levels = Column(Integer)
    amount_per_grid = Column(Float)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    
class DCABot(Base):
    __tablename__ = "dca_bots"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    amount_per_period = Column(Float)
    interval_days = Column(Integer)
    total_periods = Column(Integer)
    completed_periods = Column(Integer, default=0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    next_buy_date = Column(DateTime, nullable=True)
    
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    details = Column(Text)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class BotConfig(Base):
    """การตั้งค่า Auto Trading Bot"""
    __tablename__ = 'bot_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, default=1)  # สำหรับ multi-user ในอนาคต
    
    # Bot Settings
    name = Column(String, default="Auto Bot")  # ชื่อ Bot
    symbol = Column(String, default="BTC/USDT")  # 'BTC/USDT'
    is_active = Column(Boolean, default=False)  # เปิด/ปิด Bot
    
    # Budget & Risk
    budget = Column(Float, default=10000.0)  # งบประมาณ (USD)
    position_size_ratio = Column(Float, default=0.95)  # ใช้เงิน 95%
    min_confidence = Column(Float, default=0.7)  # AI Confidence threshold
    
    # Risk Level (Conservative/Moderate/Aggressive)
    risk_level = Column(String, default='moderate')
    max_daily_loss = Column(Float, default=5.0)  # ขาดทุนสูงสุด/วัน (%)
    max_open_positions = Column(Integer, default=1)  # จำนวน position พร้อมกัน
    
    # Notification
    enable_notifications = Column(Boolean, default=True)
    telegram_chat_id = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert BotConfig to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'budget': self.budget,
            'risk_level': self.risk_level,
            'min_confidence': self.min_confidence,
            'position_size_ratio': self.position_size_ratio,
            'max_daily_loss': self.max_daily_loss,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

