import axios from 'axios'

const API_BASE = (import.meta as any).env?.PROD ? '/api' : 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface AIDecision {
  action: 'BUY' | 'SELL' | 'HOLD' | 'HALT'
  principle: string
  predicted_pl_percent: number
  confidence: number
  scores: {
    market: number
    fundamental: number
    sentiment: number
    whale: number
  }
  timestamp: string
  symbol: string
}

export interface TradeRequest {
  symbol: string
  side: 'BUY' | 'SELL'
  amount: number
  price?: number
}

export interface GridBotConfig {
  symbol: string
  lower_price: number
  upper_price: number
  grid_levels: number
  amount_per_grid: number
}

export interface DCABotConfig {
  symbol: string
  amount_per_period: number
  interval_days: number
  total_periods: number
}

export interface MarketData {
  symbol: string
  price: number
  change_24h: number
  volume_24h: number
  high_24h: number
  low_24h: number
  ohlcv: number[][]
  currency: string
}

export interface WhaleData {
  symbol: string
  movements: Array<{
    timestamp: string
    amount: number
    type: string
    wallet: string
    usd_value: number
  }>
  whale_score: number
  net_flow: number
  interpretation: string
}

export interface Portfolio {
  total_trades: number
  total_invested: number
  total_returns: number
  profit_loss: number
  roi_percent: number
}

export interface PerformanceData {
  period: 'today' | 'week' | 'month' | 'year'
  has_data: boolean
  profit_loss: number
  profit_loss_percent: number
  total_trades: number
  completed_rounds: number
  win_rate: number
  best_trade: number
  worst_trade: number
  total_invested: number
  start_date: string
  end_date: string
  message?: string
}

export interface RecentTrade {
  id: number
  symbol: string
  side: 'BUY' | 'SELL'
  amount: number
  price: number
  status: string
  timestamp: string
}

export interface AIForceStatus {
  is_running: boolean
  symbol: string
  daily_trades: number
  start_balance: number
  current_balance: number
  profit_loss: number
  profit_percent: number
  position_side: string | null
  entry_price: number | null
  max_profit: number
  max_loss: number
}

export interface AIForceConfig {
  symbol: string
  amount: number
  max_profit: number
  max_loss: number
}

export interface BacktestConfig {
  symbol: string
  timeframe: string
  days: number
  initial_capital: number
  position_size_percent: number
}

export interface BacktestResult {
  success: boolean
  metrics: {
    total_return_percent: number
    max_drawdown_percent: number
    sharpe_ratio: number
    sortino_ratio: number
    win_rate_percent: number
    profit_factor: number
    total_trades: number
    completed_rounds: number
    final_equity: number
  }
  equity_curve: Array<{ timestamp: string; equity: number }>
  trades: Array<any>
  config: any
}

export interface AdvancedAnalysis {
  action: 'BUY' | 'SELL' | 'HOLD' | 'HALT'
  reason: string
  confidence: number
  current_price: number
  stop_loss: number
  take_profit: number
  risk_reward_ratio: number
  modules: {
    regime: {
      regime: string
      confidence: number
      allow_mean_reversion: boolean
      adx: number
      bb_width: number
    }
    sentiment: {
      score: number
      interpretation: string
      should_trade: boolean
      twitter: number
      news: number
    }
    risk_levels: {
      stop_loss_price: number
      take_profit_price: number
      stop_loss_pct: number
      take_profit_pct: number
      atr: number
      volatility: number
    }
    reversal: {
      is_bullish_reversal: boolean
      is_bearish_reversal: boolean
      confidence: number
      patterns_detected: string[]
      order_book_imbalance: number
    }
  }
}

// API Methods
export const apiClient = {
  // Health Check
  healthCheck: () => api.get('/health'),

  // AI Decision
  getDecision: (symbol: string, currency: string = 'USD') =>
    api.get<AIDecision>(`/decision/${symbol}?currency=${currency}`),

  // Trading
  executeTrade: (trade: TradeRequest) =>
    api.post('/trade', trade),

  // Grid Bot
  startGridBot: (config: GridBotConfig) =>
    api.post(`/grid-bot/${config.symbol}`, config),

  // DCA Bot
  startDCABot: (config: DCABotConfig) =>
    api.post(`/dca-bot/${config.symbol}`, config),

  // Market Data
  getMarketData: (symbol: string, currency: string = 'USD') =>
    api.get<MarketData>(`/market/${symbol}?currency=${currency}`),

  // Whale Tracking
  getWhaleData: (symbol: string) =>
    api.get<WhaleData>(`/whale/${symbol}`),

  // Portfolio
  getPortfolio: () =>
    api.get<Portfolio>('/portfolio'),

  // Performance
  getPerformance: (period: 'today' | 'week' | 'month' | 'year') =>
    api.get<PerformanceData>(`/performance/${period}`),

  // Recent Trades
  getRecentTrades: (limit: number = 10) =>
    api.get<{ trades: RecentTrade[] }>(`/performance/recent-trades?limit=${limit}`),

  // Account Balance
  getAccountBalance: () =>
    api.get<{ balances: Array<{ asset: string; free: string; locked: string }> }>('/account/balance'),

  // AI Force Trading Bot
  startAIForceBot: (config: AIForceConfig) =>
    api.post('/bot/ai-force/start', null, { params: config }),

  stopAIForceBot: () =>
    api.post('/bot/ai-force/stop'),

  getAIForceStatus: () =>
    api.get<AIForceStatus>('/bot/ai-force/status'),

  getAdvancedAnalysis: (symbol: string, currency: string = 'USD') =>
    api.get<AdvancedAnalysis>(`/advanced-analysis/${symbol}?currency=${currency}`),

  // Backtesting
  runBacktest: (config: BacktestConfig) =>
    api.post<BacktestResult>('/backtest/run', config),

  getBacktestPresets: () =>
    api.get('/backtest/presets'),

  analyzeOnChain: (symbol: string) =>
    api.get(`/onchain/analyze?symbol=${symbol}`),
}

export type ApiClient = typeof apiClient

export default apiClient
