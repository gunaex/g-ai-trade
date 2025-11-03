import axios from 'axios'

// Production API URL from Render
// Development uses relative '/api' via Vite proxy
const API_BASE: string = (import.meta as any).env?.VITE_API_URL || 'https://g-ai-trade-backend.onrender.com/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and we haven't retried yet, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const data = response.data as { access_token: string; refresh_token: string }
          const { access_token, refresh_token: newRefreshToken } = data
          
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', newRefreshToken)

          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)

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

// ============================================================================
// AUTO BOT INTERFACES
// ============================================================================

export interface AutoBotConfig {
  id?: number
  name: string
  symbol: string
  budget: number
  risk_level: 'conservative' | 'moderate' | 'aggressive'
  min_confidence: number
  position_size_ratio: number
  max_daily_loss: number
}

export interface AutoBotStatus {
  is_running: boolean
  ai_modules: {
    brain: number
    decision: number
    ml: number
    network: number
    nlp: number
    perception: number
    learning: number
  }
  current_position: {
    trade_id: number
    entry_price: number
    quantity: number
    entry_time: string
  } | null
  last_check: string | null
  symbol?: string
  budget?: number
  activity_log?: Array<{
    timestamp: string
    message: string
    level: string
    data: any
  }>
  config?: any
  performance?: {
    total_pnl: number
    total_trades: number
    win_trades: number
    loss_trades: number
    win_rate: number
    total_fees: number
    open_position_value: number
  }
}

export interface AutoBotPerformance {
  total_pnl: number
  total_trades: number
  recent_trades: Array<{
    timestamp: string
    symbol: string
    side: string
    price: number
    amount: number
  }>
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
    api.get<AdvancedAnalysis>(`/advanced-analysis/${symbol}?currency=${currency}`, { timeout: 20000 }),

  // Backtesting
  runBacktest: (config: BacktestConfig) =>
    api.post<BacktestResult>('/backtest/run', config),

  getBacktestPresets: () =>
    api.get('/backtest/presets'),

  analyzeOnChain: (symbol: string) =>
    api.get(`/onchain/analyze?symbol=${symbol}`),

  // Auto Bot APIs
  createAutoBotConfig: (config: AutoBotConfig) =>
    api.post('/auto-bot/create', config),

  getAutoBotConfig: (configId: number) =>
    api.get<AutoBotConfig>(`/auto-bot/config/${configId}`),

  startAutoBot: (configId: number) =>
    api.post(`/auto-bot/start/${configId}`),

  stopAutoBot: (configId: number) =>
    api.post(`/auto-bot/stop/${configId}`),

  getAutoBotStatus: () =>
    api.get<AutoBotStatus>('/auto-bot/status'),

  getAutoBotPerformance: () =>
    api.get<AutoBotPerformance>('/auto-bot/performance'),

  // Authentication
  register: (username: string, email: string, password: string) =>
    api.post('/auth/register', { username, email, password }),

  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),

  refreshToken: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),

  getCurrentUser: () =>
    api.get('/auth/me'),

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  },

  // API Key Management
  saveApiKeys: (binanceApiKey: string, binanceApiSecret: string) =>
    api.post('/auth/api-keys', { binance_api_key: binanceApiKey, binance_api_secret: binanceApiSecret }),

  getApiKeysStatus: () =>
    api.get<{ has_api_keys: boolean; api_key_preview: string | null }>('/auth/api-keys/status'),

  deleteApiKeys: () =>
    api.delete('/auth/api-keys'),
}

export type ApiClient = typeof apiClient

export default apiClient
