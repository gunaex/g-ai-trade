"""
Example Script สำหรับทดสอบ Backtesting
"""

import asyncio
import sys
import os

# เพิ่ม path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.backtesting.backtesting_engine import (
    BacktestingEngine,
    load_historical_data
)
from app.backtesting.onchain_filter import (
    OnChainFilter,
    MockOnChainProvider
)
from app.ai.advanced_modules import AdvancedAITradingEngine
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_backtest_quick():
    """
    ทดสอบ Backtest แบบเร็ว (7 วัน, 5m timeframe)
    """
    logger.info("="*60)
    logger.info("QUICK BACKTEST TEST (7 days, 5m)")
    logger.info("="*60)
    
    # 1. โหลดข้อมูล
    symbol = 'BTC/USDT'
    data = await load_historical_data(symbol, timeframe='5m', days=7)
    
    logger.info(f"Loaded {len(data)} bars")
    
    if data.empty:
        logger.error("No data loaded!")
        return
    
    # 2. สร้าง AI Engine
    ai_engine = AdvancedAITradingEngine()
    
    # 3. สร้าง Backtesting Engine
    backtest = BacktestingEngine(
        symbol=symbol,
        data=data,
        ai_engine=ai_engine,
        initial_capital=10000,
        position_size_percent=0.95
    )
    
    # 4. รัน Backtest (asynchronous)
    metrics = await backtest.run()
    
    # 5. แสดงผล
    backtest.generate_tear_sheet()
    
    return metrics


async def test_onchain_filter():
    """
    ทดสอบ On-Chain Filter
    """
    logger.info("\n" + "="*60)
    logger.info("ON-CHAIN FILTER TEST")
    logger.info("="*60)
    
    # สร้าง Filter (ใช้ Mock Provider)
    onchain_filter = OnChainFilter(provider=MockOnChainProvider())
    
    # วิเคราะห์
    symbol = 'BTC/USDT'
    analysis = await onchain_filter.analyze(symbol)
    
    logger.info(f"\nSymbol: {symbol}")
    logger.info(f"Status: {analysis.status}")
    logger.info(f"Confidence: {analysis.confidence:.2f}")
    logger.info(f"Veto Buy: {analysis.veto_buy}")
    logger.info(f"Reasoning: {analysis.reasoning}")
    logger.info(f"\nMetrics:")
    logger.info(f"  Exchange Netflow: {analysis.metrics.exchange_netflow:.2f}")
    logger.info(f"  Whale Transactions: {analysis.metrics.whale_transactions}")
    logger.info(f"  Whale Volume: {analysis.metrics.whale_volume:.2f}")
    logger.info(f"  SSR: {analysis.metrics.stablecoin_supply_ratio:.3f}")
    
    return analysis


async def main():
    """
    Main test runner
    """
    try:
        # Test 1: Quick Backtest
        logger.info("\n🚀 Starting Test 1: Quick Backtest")
        await test_backtest_quick()
        
        # Test 2: On-Chain Filter
        logger.info("\n🚀 Starting Test 2: On-Chain Filter")
        await test_onchain_filter()
        
        logger.info("\n✅ All tests completed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
