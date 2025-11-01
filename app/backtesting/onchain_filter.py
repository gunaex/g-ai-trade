"""
On-Chain Data Filter (Module 5)
ตรวจจับการสะสม/เทขายของ Smart Money
มี Veto Power ในการยับยั้งสัญญาณซื้อ
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Literal
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ON-CHAIN STATUS
# ============================================================================

OnChainStatus = Literal['ACCUMULATION', 'DISTRIBUTION', 'NEUTRAL']


@dataclass
class OnChainMetrics:
    """Key On-Chain Metrics"""
    exchange_netflow: float  # + = outflow (bullish), - = inflow (bearish)
    whale_transactions: int
    whale_volume: float
    stablecoin_supply_ratio: float
    timestamp: datetime


@dataclass
class OnChainAnalysis:
    """ผลการวิเคราะห์ On-Chain"""
    status: OnChainStatus
    confidence: float  # 0-1
    metrics: OnChainMetrics
    reasoning: str
    veto_buy: bool  # True = ห้ามซื้อ


# ============================================================================
# ON-CHAIN DATA PROVIDERS
# ============================================================================

class OnChainDataProvider:
    """
    Base class สำหรับ On-Chain Data Providers
    """
    
    def get_exchange_netflow(self, symbol: str, hours: int = 24) -> float:
        """
        Exchange Netflow (Inflow - Outflow)
        + = Outflow (เงินไหลออก Exchange = Bullish)
        - = Inflow (เงินไหลเข้า Exchange = Bearish)
        """
        raise NotImplementedError
    
    def get_whale_activity(self, symbol: str, hours: int = 24) -> Dict:
        """
        Whale Transactions (ธุรกรรมใหญ่)
        """
        raise NotImplementedError
    
    def get_stablecoin_supply_ratio(self) -> float:
        """
        Stablecoin Supply Ratio (SSR)
        """
        raise NotImplementedError


class MockOnChainProvider(OnChainDataProvider):
    """
    Mock Provider สำหรับทดสอบ
    (ใช้ข้อมูลจำลอง)
    """
    
    def get_exchange_netflow(self, symbol: str, hours: int = 24) -> float:
        # Mock: สุ่มค่า -1000 ถึง +1000 BTC
        return np.random.uniform(-1000, 1000)
    
    def get_whale_activity(self, symbol: str, hours: int = 24) -> Dict:
        # Mock: สุ่มจำนวนธุรกรรม
        return {
            'transaction_count': np.random.randint(5, 50),
            'total_volume': np.random.uniform(100, 5000)
        }
    
    def get_stablecoin_supply_ratio(self) -> float:
        # Mock: สุ่ม SSR 0.05 - 0.15
        return np.random.uniform(0.05, 0.15)


class GlassnodeProvider(OnChainDataProvider):
    """
    Glassnode API Provider
    (ต้องมี API Key)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics"
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """ส่ง API request"""
        try:
            params['api_key'] = self.api_key
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Glassnode API error: {e}")
            return None
    
    def get_exchange_netflow(self, symbol: str, hours: int = 24) -> float:
        """
        Exchange Netflow
        Endpoint: /distribution/exchange_net_position_change
        """
        # แปลง symbol (BTCUSDT -> BTC)
        asset = symbol.replace('USDT', '').replace('BUSD', '')
        
        since = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())
        
        data = self._make_request(
            "distribution/exchange_net_position_change",
            params={
                'a': asset,
                's': since,
                'i': '24h'
            }
        )
        
        if data and len(data) > 0:
            # ค่าล่าสุด
            return float(data[-1]['v'])
        
        return 0.0
    
    def get_whale_activity(self, symbol: str, hours: int = 24) -> Dict:
        """
        Whale Transactions
        Endpoint: /transactions/transfers_volume_sum
        """
        asset = symbol.replace('USDT', '').replace('BUSD', '')
        
        since = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())
        
        # Transactions > $100k
        data = self._make_request(
            "transactions/transfers_volume_sum",
            params={
                'a': asset,
                's': since,
                'i': '1h'
            }
        )
        
        if data:
            return {
                'transaction_count': len(data),
                'total_volume': sum(float(d['v']) for d in data if d['v'])
            }
        
        return {'transaction_count': 0, 'total_volume': 0.0}
    
    def get_stablecoin_supply_ratio(self) -> float:
        """
        Stablecoin Supply Ratio
        """
        # ใช้ Mock แทน (Glassnode ไม่มี endpoint ตรงนี้)
        return np.random.uniform(0.05, 0.15)


# ============================================================================
# ON-CHAIN FILTER
# ============================================================================

class OnChainFilter:
    """
    Module 5: On-Chain Data Filter
    
    Features:
    - ตรวจจับการสะสม/เทขาย (ACCUMULATION/DISTRIBUTION)
    - มี Veto Power ยับยั้งสัญญาณซื้อ
    - Integration กับ AI Pipeline
    """
    
    def __init__(self, provider: OnChainDataProvider = None):
        self.provider = provider or MockOnChainProvider()
        
        # Thresholds
        self.netflow_accumulation_threshold = 500   # BTC ไหลออก > 500 = ACCUMULATION
        self.netflow_distribution_threshold = -500  # BTC ไหลเข้า < -500 = DISTRIBUTION
        self.whale_volume_threshold = 1000          # Whale volume > 1000 BTC
    
    async def analyze(self, symbol: str) -> OnChainAnalysis:
        """
        วิเคราะห์สถานะ On-Chain
        """
        try:
            # ดึง Metrics
            netflow = self.provider.get_exchange_netflow(symbol, hours=24)
            whale_activity = self.provider.get_whale_activity(symbol, hours=24)
            ssr = self.provider.get_stablecoin_supply_ratio()
            
            metrics = OnChainMetrics(
                exchange_netflow=netflow,
                whale_transactions=whale_activity['transaction_count'],
                whale_volume=whale_activity['total_volume'],
                stablecoin_supply_ratio=ssr,
                timestamp=datetime.utcnow()
            )
            
            # ตัดสินสถานะ
            status, confidence, reasoning = self._determine_status(metrics)
            
            # Veto Power
            veto_buy = (status == 'DISTRIBUTION')
            
            return OnChainAnalysis(
                status=status,
                confidence=confidence,
                metrics=metrics,
                reasoning=reasoning,
                veto_buy=veto_buy
            )
            
        except Exception as e:
            logger.error(f"OnChain analysis error: {e}")
            # Default: NEUTRAL
            return OnChainAnalysis(
                status='NEUTRAL',
                confidence=0.5,
                metrics=OnChainMetrics(0, 0, 0, 0.1, datetime.utcnow()),
                reasoning=f"Error: {str(e)}",
                veto_buy=False
            )
    
    def _determine_status(self, metrics: OnChainMetrics) -> tuple:
        """
        ตัดสินสถานะ On-Chain
        Returns: (status, confidence, reasoning)
        """
        score = 0
        reasons = []
        
        # 1. Exchange Netflow
        if metrics.exchange_netflow > self.netflow_accumulation_threshold:
            score += 2
            reasons.append(f"Netflow: +{metrics.exchange_netflow:.0f} (Outflow = Accumulation)")
        elif metrics.exchange_netflow < self.netflow_distribution_threshold:
            score -= 2
            reasons.append(f"Netflow: {metrics.exchange_netflow:.0f} (Inflow = Distribution)")
        else:
            reasons.append(f"Netflow: {metrics.exchange_netflow:.0f} (Neutral)")
        
        # 2. Whale Activity
        if metrics.whale_volume > self.whale_volume_threshold:
            if metrics.exchange_netflow < 0:  # ไหลเข้า Exchange
                score -= 1
                reasons.append(f"Whales moving {metrics.whale_volume:.0f} TO exchanges (Bearish)")
            else:
                score += 1
                reasons.append(f"Whales moving {metrics.whale_volume:.0f} FROM exchanges (Bullish)")
        
        # 3. Stablecoin Supply Ratio
        if metrics.stablecoin_supply_ratio > 0.12:
            score += 1
            reasons.append(f"SSR: {metrics.stablecoin_supply_ratio:.3f} (High buying power)")
        elif metrics.stablecoin_supply_ratio < 0.07:
            score -= 1
            reasons.append(f"SSR: {metrics.stablecoin_supply_ratio:.3f} (Low buying power)")
        
        # Determine status
        if score >= 2:
            status = 'ACCUMULATION'
            confidence = min(0.9, 0.5 + score * 0.1)
        elif score <= -2:
            status = 'DISTRIBUTION'
            confidence = min(0.9, 0.5 + abs(score) * 0.1)
        else:
            status = 'NEUTRAL'
            confidence = 0.5
        
        reasoning = " | ".join(reasons)
        
        return status, confidence, reasoning


# ============================================================================
# INTEGRATION: UPDATED AI PIPELINE
# ============================================================================

class IntegratedDecisionEngine:
    """
    Updated AI Pipeline with On-Chain Filter (Module 5)
    
    Pipeline:
    1. Market Regime Filter
    2. On-Chain Filter (NEW) ← มี Veto Power
    3. Sentiment Analysis
    4. Pattern Recognition
    5. Dynamic Risk Management
    """
    
    def __init__(self, 
                 market_regime_filter,
                 onchain_filter: OnChainFilter,
                 sentiment_analyzer,
                 pattern_recognizer,
                 risk_manager):
        self.market_regime = market_regime_filter
        self.onchain = onchain_filter
        self.sentiment = sentiment_analyzer
        self.pattern = pattern_recognizer
        self.risk = risk_manager
    
    async def analyze(self, symbol: str, ohlcv_data) -> Dict:
        """
        Hierarchical Decision Pipeline with On-Chain Filter
        """
        try:
            # Step 1: Market Regime Filter
            regime = await self.market_regime.detect_regime(ohlcv_data)
            
            if regime == 'SIDEWAYS':
                return {
                    'decision': 'HALT',
                    'confidence': 0.9,
                    'reasoning': 'Market regime is SIDEWAYS (not tradeable)'
                }
            
            # Step 2: On-Chain Filter (NEW) ← Veto Power
            onchain_analysis = await self.onchain.analyze(symbol)
            
            # 🔴 VETO POWER: ถ้า DISTRIBUTION ห้ามซื้อทันที
            if onchain_analysis.veto_buy:
                return {
                    'decision': 'HALT',
                    'confidence': onchain_analysis.confidence,
                    'reasoning': f'On-Chain VETO: {onchain_analysis.reasoning}',
                    'onchain_status': onchain_analysis.status
                }
            
            # Step 3: Sentiment Analysis
            sentiment_score = await self.sentiment.analyze(symbol)
            
            if sentiment_score < 0:
                return {
                    'decision': 'HOLD',
                    'confidence': 0.7,
                    'reasoning': 'Negative sentiment detected'
                }
            
            # Step 4: Pattern Recognition
            pattern_signal = await self.pattern.detect_patterns(ohlcv_data)
            
            if not pattern_signal:
                return {
                    'decision': 'HOLD',
                    'confidence': 0.6,
                    'reasoning': 'No clear pattern detected'
                }
            
            # Step 5: Dynamic Risk Management
            risk_assessment = await self.risk.assess(symbol, pattern_signal)
            
            # Final Decision
            if risk_assessment['approved']:
                return {
                    'decision': 'BUY',
                    'confidence': 0.8,
                    'reasoning': f"All checks passed | OnChain: {onchain_analysis.status} | Pattern: {pattern_signal}",
                    'onchain_status': onchain_analysis.status,
                    'take_profit': risk_assessment['take_profit'],
                    'stop_loss': risk_assessment['stop_loss']
                }
            else:
                return {
                    'decision': 'HOLD',
                    'confidence': 0.6,
                    'reasoning': 'Risk assessment rejected trade'
                }
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return {
                'decision': 'HALT',
                'confidence': 0,
                'reasoning': f'Error: {str(e)}'
            }
