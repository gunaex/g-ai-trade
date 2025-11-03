"""
Example: How to Use the New Advanced AI Features in Trading Bot

This file demonstrates how to integrate the new AI improvements
into your existing trading systems (AI Force Bot, God's Hand, etc.)
"""

import asyncio
import pandas as pd
from datetime import datetime
from app.binance_client import get_market_data_client
from app.ai.advanced_modules import AdvancedAITradingEngine
from app.ai.risk_management import AdaptiveStopLoss, PerformanceTracker

# ===========================================================================
# Example 1: Enhanced AI Force Bot with New Features
# ===========================================================================

class EnhancedAIForceBot:
    """
    AI Force Bot with all new improvements:
    - Dynamic position sizing
    - Multi-timeframe analysis
    - Real volume analysis
    - Adaptive trailing stops
    - Performance tracking
    """
    
    def __init__(self, api_key: str, api_secret: str):
        self.market_client = get_market_data_client()
        self.ai_engine = AdvancedAITradingEngine(market_client=self.market_client)
        self.performance_tracker = PerformanceTracker()
        
        # Trading state
        self.is_running = False
        self.current_position = None
        self.adaptive_stop = None
        self.account_balance = 10000.0  # Initialize from API
        
    async def analyze_and_trade(self, symbol: str):
        """
        Complete analysis and trade execution with new features
        """
        try:
            # 1. Fetch OHLCV data
            ohlcv = self.market_client.fetch_ohlcv(symbol, '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 2. Fetch order book for liquidity check
            order_book = self.market_client.fetch_order_book(symbol)
            
            # 3. Run comprehensive AI analysis
            analysis = self.ai_engine.analyze(
                symbol=symbol,
                ohlcv=df,
                order_book=order_book,
                account_balance=self.account_balance
            )
            
            # 4. Log analysis results
            print(f"\n{'='*60}")
            print(f"AI Analysis for {symbol}")
            print(f"{'='*60}")
            print(f"Action: {analysis['action']}")
            print(f"Confidence: {analysis['confidence']*100:.1f}%")
            print(f"Reason: {analysis['reason']}")
            print(f"Current Price: ${analysis['current_price']:.2f}")
            print(f"Position Size: ${analysis['position_size_usd']:.2f} ({analysis['position_pct']:.2f}%)")
            print(f"Stop Loss: ${analysis['stop_loss']:.2f}")
            print(f"Take Profit: ${analysis['take_profit']:.2f}")
            print(f"Risk/Reward: {analysis['risk_reward_ratio']:.2f}")
            
            # Multi-timeframe info
            if analysis['modules'].get('mtf'):
                mtf = analysis['modules']['mtf']
                print(f"\nMulti-Timeframe: {mtf['alignment']}")
                print(f"Timeframes Analyzed: {mtf['timeframes_analyzed']}")
            
            # Volume analysis info
            volume = analysis['modules']['volume']
            print(f"\nVolume Analysis: {volume['interpretation']}")
            print(f"Volume Score: {volume['score']:.2f}")
            if volume.get('vwap'):
                print(f"Price vs VWAP: {volume['vwap'].get('price_vs_vwap_pct', 0):.2f}%")
            
            # Performance stats
            perf = analysis['modules']['performance']
            print(f"\nPerformance Stats (30d):")
            print(f"Win Rate: {perf['win_rate']*100:.1f}%")
            print(f"Profit Factor: {perf['profit_factor']:.2f}")
            print(f"Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
            print(f"Max Drawdown: {perf['max_drawdown_pct']:.2f}%")
            
            # 5. Execute trading decision
            await self._execute_decision(analysis, symbol, df)
            
        except Exception as e:
            print(f"Error in analyze_and_trade: {e}")
            import traceback
            traceback.print_exc()
    
    async def _execute_decision(self, analysis: dict, symbol: str, ohlcv: pd.DataFrame):
        """
        Execute trading decision with new risk management
        """
        action = analysis['action']
        confidence = analysis['confidence']
        current_price = analysis['current_price']
        
        # Only trade if confidence > 60%
        if confidence < 0.6:
            print(f"\n⏸️  Confidence too low ({confidence*100:.1f}%) - HOLD")
            return
        
        # BUY Signal
        if action == 'BUY' and not self.current_position:
            print(f"\n🟢 EXECUTING BUY")
            
            # Calculate position size (already calculated by AI)
            position_size_usd = analysis['position_size_usd']
            quantity = position_size_usd / current_price
            
            # Check liquidity (if available)
            if 'liquidity' in analysis['modules']:
                liq = analysis['modules']['liquidity']
                if not liq['is_tradeable']:
                    print(f"⚠️  Insufficient liquidity: {liq['warning']}")
                    return
            
            # Execute buy order (mock for example)
            print(f"   Order: BUY {quantity:.6f} {symbol} at ${current_price:.2f}")
            print(f"   Position Size: ${position_size_usd:.2f}")
            
            # Initialize adaptive stop loss
            self.adaptive_stop = AdaptiveStopLoss(
                entry_price=current_price,
                side='BUY',
                atr_multiplier=2.5
            )
            
            # Update stop immediately
            stop_info = self.adaptive_stop.update_stop(ohlcv, current_price)
            print(f"   Initial Stop: ${stop_info['stop_loss_price']:.2f} ({stop_info['stop_distance_pct']:.2f}% away)")
            print(f"   Take Profit: ${analysis['take_profit']:.2f}")
            
            # Store position info
            self.current_position = {
                'symbol': symbol,
                'side': 'BUY',
                'entry_price': current_price,
                'quantity': quantity,
                'entry_time': datetime.now(),
                'stop_loss': stop_info['stop_loss_price'],
                'take_profit': analysis['take_profit']
            }
            
            print(f"✅ Position opened successfully")
        
        # SELL Signal (close BUY position)
        elif action == 'SELL' and self.current_position and self.current_position['side'] == 'BUY':
            print(f"\n🔴 EXECUTING SELL (Close Position)")
            
            position = self.current_position
            exit_price = current_price
            
            # Calculate P&L
            pnl_usd = (exit_price - position['entry_price']) * position['quantity']
            pnl_pct = ((exit_price - position['entry_price']) / position['entry_price']) * 100
            
            print(f"   Entry: ${position['entry_price']:.2f}")
            print(f"   Exit: ${exit_price:.2f}")
            print(f"   P&L: ${pnl_usd:+.2f} ({pnl_pct:+.2f}%)")
            
            # Log trade for performance tracking
            hold_time = (datetime.now() - position['entry_time']).total_seconds() / 60
            
            self.performance_tracker.log_trade({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': position['side'],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'quantity': position['quantity'],
                'pnl_usd': pnl_usd,
                'pnl_pct': pnl_pct,
                'confidence': confidence,
                'regime': analysis['modules']['regime']['regime'],
                'hold_time_minutes': hold_time
            })
            
            # Update account balance
            self.account_balance += pnl_usd
            
            # Clear position
            self.current_position = None
            self.adaptive_stop = None
            
            print(f"✅ Position closed successfully")
            print(f"   New Balance: ${self.account_balance:.2f}")
    
    async def monitor_position(self, symbol: str):
        """
        Monitor open position with adaptive stop loss
        """
        if not self.current_position or not self.adaptive_stop:
            return
        
        try:
            # Fetch latest data
            ohlcv = self.market_client.fetch_ohlcv(symbol, '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            current_price = df['close'].iloc[-1]
            
            # Update adaptive stop
            stop_info = self.adaptive_stop.update_stop(df, current_price)
            
            print(f"\n📊 Position Monitor - {symbol}")
            print(f"   Current: ${current_price:.2f}")
            print(f"   Entry: ${self.current_position['entry_price']:.2f}")
            print(f"   Stop: ${stop_info['stop_loss_price']:.2f} ({stop_info['method_used']})")
            print(f"   Take Profit: ${self.current_position['take_profit']:.2f}")
            
            # Calculate unrealized P&L
            unrealized_pnl = (current_price - self.current_position['entry_price']) * self.current_position['quantity']
            unrealized_pnl_pct = ((current_price - self.current_position['entry_price']) / self.current_position['entry_price']) * 100
            print(f"   Unrealized P&L: ${unrealized_pnl:+.2f} ({unrealized_pnl_pct:+.2f}%)")
            
            # Check if stop hit
            should_exit, reason = self.adaptive_stop.should_exit(current_price)
            if should_exit:
                print(f"\n🛑 STOP LOSS HIT: {reason}")
                # Execute exit (would trigger SELL logic)
                await self._execute_stop_loss(symbol, current_price)
            
            # Check if take profit hit
            if current_price >= self.current_position['take_profit']:
                print(f"\n🎯 TAKE PROFIT HIT: ${current_price:.2f} >= ${self.current_position['take_profit']:.2f}")
                await self._execute_take_profit(symbol, current_price)
                
        except Exception as e:
            print(f"Error monitoring position: {e}")
    
    async def _execute_stop_loss(self, symbol: str, exit_price: float):
        """Execute stop loss exit"""
        if not self.current_position:
            return
        
        position = self.current_position
        pnl_usd = (exit_price - position['entry_price']) * position['quantity']
        pnl_pct = ((exit_price - position['entry_price']) / position['entry_price']) * 100
        
        print(f"   Exit Price: ${exit_price:.2f}")
        print(f"   Loss: ${pnl_usd:+.2f} ({pnl_pct:+.2f}%)")
        
        # Log trade
        hold_time = (datetime.now() - position['entry_time']).total_seconds() / 60
        self.performance_tracker.log_trade({
            'timestamp': datetime.now(),
            'symbol': symbol,
            'side': position['side'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'quantity': position['quantity'],
            'pnl_usd': pnl_usd,
            'pnl_pct': pnl_pct,
            'confidence': 0.0,  # Stop loss exit
            'regime': 'STOP_LOSS',
            'hold_time_minutes': hold_time
        })
        
        self.account_balance += pnl_usd
        self.current_position = None
        self.adaptive_stop = None
        
        print(f"✅ Stop loss executed. Balance: ${self.account_balance:.2f}")
    
    async def _execute_take_profit(self, symbol: str, exit_price: float):
        """Execute take profit exit"""
        if not self.current_position:
            return
        
        position = self.current_position
        pnl_usd = (exit_price - position['entry_price']) * position['quantity']
        pnl_pct = ((exit_price - position['entry_price']) / position['entry_price']) * 100
        
        print(f"   Exit Price: ${exit_price:.2f}")
        print(f"   Profit: ${pnl_usd:+.2f} ({pnl_pct:+.2f}%)")
        
        # Log trade
        hold_time = (datetime.now() - position['entry_time']).total_seconds() / 60
        self.performance_tracker.log_trade({
            'timestamp': datetime.now(),
            'symbol': symbol,
            'side': position['side'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'quantity': position['quantity'],
            'pnl_usd': pnl_usd,
            'pnl_pct': pnl_pct,
            'confidence': 1.0,  # Take profit hit
            'regime': 'TAKE_PROFIT',
            'hold_time_minutes': hold_time
        })
        
        self.account_balance += pnl_usd
        self.current_position = None
        self.adaptive_stop = None
        
        print(f"✅ Take profit executed. Balance: ${self.account_balance:.2f}")
    
    async def trading_loop(self, symbol: str):
        """
        Main trading loop
        """
        self.is_running = True
        
        while self.is_running:
            try:
                # Analyze market and execute if needed
                await self.analyze_and_trade(symbol)
                
                # Monitor existing position
                if self.current_position:
                    await self.monitor_position(symbol)
                
                # Wait before next iteration
                await asyncio.sleep(60)  # 1 minute
                
            except Exception as e:
                print(f"Error in trading loop: {e}")
                await asyncio.sleep(60)
        
        print("Trading loop stopped")


# ===========================================================================
# Example 2: Quick Test of New Features
# ===========================================================================

async def quick_test():
    """
    Quick test of all new features
    """
    print("🚀 Testing New AI Features\n")
    
    # Initialize
    market_client = get_market_data_client()
    ai_engine = AdvancedAITradingEngine(market_client=market_client)
    
    # Test symbol
    symbol = 'BTC/USDT'
    
    # Fetch data
    print(f"Fetching data for {symbol}...")
    ohlcv = market_client.fetch_ohlcv(symbol, '1h', limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    order_book = market_client.fetch_order_book(symbol)
    
    # Run analysis
    print("Running AI analysis...")
    result = ai_engine.analyze(
        symbol=symbol,
        ohlcv=df,
        order_book=order_book,
        account_balance=10000.0
    )
    
    # Display results
    print(f"\n{'='*70}")
    print(f"AI ANALYSIS RESULTS")
    print(f"{'='*70}")
    print(f"Symbol: {symbol}")
    print(f"Action: {result['action']}")
    print(f"Confidence: {result['confidence']*100:.1f}%")
    print(f"Reason: {result['reason']}")
    print(f"\nPrice & Risk:")
    print(f"  Current Price: ${result['current_price']:.2f}")
    print(f"  Stop Loss: ${result['stop_loss']:.2f}")
    print(f"  Take Profit: ${result['take_profit']:.2f}")
    print(f"  Risk/Reward: {result['risk_reward_ratio']:.2f}")
    print(f"\nPosition Sizing:")
    print(f"  Position Size: ${result['position_size_usd']:.2f}")
    print(f"  Position %: {result['position_pct']:.2f}%")
    
    # Module details
    print(f"\n{'='*70}")
    print(f"MODULE DETAILS")
    print(f"{'='*70}")
    
    # Regime
    regime = result['modules']['regime']
    print(f"\n1. Market Regime:")
    print(f"   Regime: {regime['regime']}")
    print(f"   ADX: {regime['adx']:.2f}")
    print(f"   BB Width: {regime['bb_width']:.4f}")
    
    # Multi-Timeframe
    if result['modules'].get('mtf'):
        mtf = result['modules']['mtf']
        print(f"\n2. Multi-Timeframe Analysis:")
        print(f"   Alignment: {mtf['alignment']}")
        print(f"   Confidence: {mtf['confidence']*100:.1f}%")
        print(f"   Timeframes Analyzed: {mtf['timeframes_analyzed']}")
    
    # Volume
    volume = result['modules']['volume']
    print(f"\n3. Volume Analysis:")
    print(f"   Score: {volume['score']:.2f}")
    print(f"   Interpretation: {volume['interpretation']}")
    if volume.get('vwap'):
        print(f"   Price vs VWAP: {volume['vwap'].get('price_vs_vwap_pct', 0):+.2f}%")
    if volume.get('obv'):
        print(f"   OBV Trend: {volume['obv'].get('trend', 'N/A')}")
    
    # Performance
    perf = result['modules']['performance']
    print(f"\n4. Performance Stats (30 days):")
    print(f"   Total Trades: {perf['total_trades']}")
    print(f"   Win Rate: {perf['win_rate']*100:.1f}%")
    print(f"   Profit Factor: {perf['profit_factor']:.2f}")
    print(f"   Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
    print(f"   Max Drawdown: {perf['max_drawdown_pct']:.2f}%")
    
    # Position Sizing
    pos = result['modules']['position_sizing']
    print(f"\n5. Position Sizing:")
    print(f"   Kelly Fraction: {pos['kelly_fraction']*100:.2f}%")
    print(f"   Volatility Multiplier: {pos['volatility_multiplier']:.2f}")
    print(f"   Confidence Multiplier: {pos['confidence_multiplier']:.2f}")
    
    print(f"\n{'='*70}")
    print("Test completed successfully! ✅")


# ===========================================================================
# Main Entry Point
# ===========================================================================

if __name__ == "__main__":
    # Run quick test
    asyncio.run(quick_test())
    
    # Or run full bot
    # bot = EnhancedAIForceBot(api_key="your_key", api_secret="your_secret")
    # asyncio.run(bot.trading_loop('BTC/USDT'))
