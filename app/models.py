from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
from app.db import Base

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
