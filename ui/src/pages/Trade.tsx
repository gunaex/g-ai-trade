import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Wallet, Power, Settings, DollarSign } from 'lucide-react'
import apiClient, { AIDecision, MarketData, AIForceStatus, AIForceConfig } from '../lib/api'
import Chart from '../components/Chart'
import AdvancedAnalysis from '../components/AdvancedAnalysis'

// Exchange rate API
const getUSDToTHBRate = async (): Promise<number> => {
  try {
    const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD')
    const data = await response.json()
    return data.rates.THB || 35.5
  } catch {
    return 35.5
  }
}

export default function Trade() {
  // Existing states
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [currency, setCurrency] = useState<'USD' | 'THB'>('USD')
  const [amount, setAmount] = useState(0.01)
  const [decision, setDecision] = useState<AIDecision | null>(null)
  const [marketData, setMarketData] = useState<MarketData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // New states
  const [usdToThbRate, setUsdToThbRate] = useState(35.5)
  const [baseCurrency, setBaseCurrency] = useState('BTC')
  const [quoteCurrency, setQuoteCurrency] = useState('USDT')
  const [balances, setBalances] = useState<Record<string, number>>({})
  const [customSymbol, setCustomSymbol] = useState('')
  const [totalPortfolioValue, setTotalPortfolioValue] = useState(0)

  // AI Force Bot states
  const [aiForceBotStatus, setAiForceBotStatus] = useState<AIForceStatus | null>(null)
  const [aiForceBotLoading, setAiForceBotLoading] = useState(false)
  const [showAIForceSettings, setShowAIForceSettings] = useState(false)
  const [aiForceVolume, setAiForceVolume] = useState(300) // THB per trade
  const [aiForceMaxProfit, setAiForceMaxProfit] = useState(6.00) // %
  const [aiForceMaxLoss, setAiForceMaxLoss] = useState(4.00) // %
  const [aiForceMinConfidence, setAiForceMinConfidence] = useState(60) // %
  const [aiForceCurrency, setAiForceCurrency] = useState<'USD' | 'THB'>('USD') // AI Bot currency

  // Trading fees
  const BINANCE_FEE_PERCENT = 0.2 // 0.1% maker + 0.1% taker

  // Popular crypto pairs
  const popularCryptos = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'XRP', 'DOGE', 'MATIC']
  const quoteOptions = ['USDT', 'USD', 'BTC', 'ETH', 'BNB']

  useEffect(() => {
    fetchExchangeRate()
    const rateInterval = setInterval(fetchExchangeRate, 300000)
    return () => clearInterval(rateInterval)
  }, [])

  useEffect(() => {
    const newSymbol = `${baseCurrency}${quoteCurrency}`
    setSymbol(newSymbol)
  }, [baseCurrency, quoteCurrency])

  useEffect(() => {
    fetchData()
    fetchBalances()
    const interval = setInterval(() => {
      fetchData()
      fetchBalances()
    }, 30000)
    return () => clearInterval(interval)
  }, [symbol, currency])

  useEffect(() => {
    if (Object.keys(balances).length > 0) {
      calculateTotalValue(balances)
    }
  }, [currency, balances, usdToThbRate, marketData])

  // Fetch AI Force Bot status
  useEffect(() => {
    if (aiForceBotStatus?.is_running) {
      const interval = setInterval(fetchAIForceStatus, 5000)
      return () => clearInterval(interval)
    }
  }, [aiForceBotStatus?.is_running])

  const fetchExchangeRate = async () => {
    const rate = await getUSDToTHBRate()
    setUsdToThbRate(rate)
  }

  const fetchBalances = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/account/balance', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (!response.ok) throw new Error('Failed to fetch balances')
      
      const data = await response.json()
      const balanceMap: Record<string, number> = {}
      
      if (data.balances && Array.isArray(data.balances)) {
        data.balances.forEach((balance: any) => {
          const asset = balance.asset
          const free = parseFloat(balance.free || 0)
          const locked = parseFloat(balance.locked || 0)
          const total = free + locked
          
          if (total > 0) {
            balanceMap[asset] = total
          }
        })
        
        setBalances(balanceMap)
        calculateTotalValue(balanceMap)
      } else {
        setBalances({})
        setTotalPortfolioValue(0)
      }
    } catch (err) {
      console.error('Failed to fetch balances:', err)
      setBalances({})
      setTotalPortfolioValue(0)
    }
  }

  const calculateTotalValue = async (balanceMap: Record<string, number>) => {
    let totalValue = 0
    
    const getCryptoPriceUSD = async (crypto: string): Promise<number> => {
      try {
        if (crypto === baseCurrency && marketData && marketData.price) {
          return marketData.price
        }
        const response = await fetch(`http://localhost:8000/api/market/${crypto}USDT?currency=USD`)
        const data = await response.json()
        return data.price || 0
      } catch {
        return 0
      }
    }
    
    for (const [crypto, balance] of Object.entries(balanceMap)) {
      if (currency === 'USD') {
        if (crypto === 'USDT' || crypto === 'USD') {
          totalValue += balance
        } else if (crypto === 'THB') {
          totalValue += balance / usdToThbRate
        } else {
          const priceUSD = await getCryptoPriceUSD(crypto)
          totalValue += balance * priceUSD
        }
      } else {
        if (crypto === 'THB') {
          totalValue += balance
        } else if (crypto === 'USDT' || crypto === 'USD') {
          totalValue += balance * usdToThbRate
        } else {
          const priceUSD = await getCryptoPriceUSD(crypto)
          totalValue += balance * priceUSD * usdToThbRate
        }
      }
    }
    
    setTotalPortfolioValue(totalValue)
  }

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [decisionRes, marketRes] = await Promise.all([
        apiClient.getDecision(symbol, currency),
        apiClient.getMarketData(symbol, currency)
      ])
      
      setDecision(decisionRes.data)
      setMarketData(marketRes.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch data')
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchAIForceStatus = async () => {
    try {
      const response = await apiClient.getAIForceStatus()
      setAiForceBotStatus(response.data)
    } catch (err) {
      console.error('Failed to fetch AI Force Bot status:', err)
    }
  }

  const handleStartAIForceBot = async () => {
    try {
      setAiForceBotLoading(true)
      
      const cryptoAmount = marketData?.price ? aiForceVolume / marketData.price : 0.01
      
      const config: AIForceConfig = {
        symbol,
        amount: cryptoAmount,
        max_profit: aiForceMaxProfit,
        max_loss: aiForceMaxLoss
      }
      
      await apiClient.startAIForceBot(config)
      await fetchAIForceStatus()
      alert('🤖 AI Force Bot Started!')
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || 'Failed to start AI Force Bot'}`)
    } finally {
      setAiForceBotLoading(false)
    }
  }

  const handleStopAIForceBot = async () => {
    try {
      setAiForceBotLoading(true)
      const response = await apiClient.stopAIForceBot()
      await fetchAIForceStatus()
      
      const data = response.data as any
      const message = `
🛑 AI Force Bot Stopped!

📊 Trading Summary:
- Round Trade: ${data.daily_trades} rounds
- Start Balance: ${data.start_balance.toFixed(2)} USDT
- Current Balance: ${data.end_balance.toFixed(2)} USDT
- Profit/Loss: ${data.profit_percent >= 0 ? '+' : ''}${data.profit_percent.toFixed(2)}%
      `
      alert(message)
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || 'Failed to stop AI Force Bot'}`)
    } finally {
      setAiForceBotLoading(false)
    }
  }

  const calculateEstimatedProfit = () => {
    if (!marketData?.price) return 0
    const volumeUSD = aiForceVolume / usdToThbRate
    const profitBeforeFees = volumeUSD * (aiForceMaxProfit / 100)
    const totalFees = volumeUSD * (BINANCE_FEE_PERCENT / 100)
    return profitBeforeFees - totalFees
  }

  const calculateEstimatedLoss = () => {
    if (!marketData?.price) return 0
    const volumeUSD = aiForceVolume / usdToThbRate
    const lossBeforeFees = volumeUSD * (aiForceMaxLoss / 100)
    const totalFees = volumeUSD * (BINANCE_FEE_PERCENT / 100)
    return lossBeforeFees + totalFees
  }

  const handleTrade = async (side: 'BUY' | 'SELL') => {
    if (!marketData) {
      alert('Market data not loaded yet')
      return
    }
    
    try {
      setLoading(true)
      await apiClient.executeTrade({
        symbol,
        side,
        amount,
        price: marketData.price
      })
      alert(`${side} order executed successfully!`)
      fetchData()
      fetchBalances()
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || 'Trade failed'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleGridBot = async () => {
    if (!marketData) {
      alert('Market data not loaded yet')
      return
    }
    
    const lowerPrice = marketData.price * 0.95
    const upperPrice = marketData.price * 1.05
    
    try {
      setLoading(true)
      await apiClient.startGridBot({
        symbol,
        lower_price: lowerPrice,
        upper_price: upperPrice,
        grid_levels: 25,
        amount_per_grid: 50
      })
      alert('Grid Bot started successfully!')
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || 'Failed to start Grid Bot'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDCABot = async () => {
    try {
      setLoading(true)
      await apiClient.startDCABot({
        symbol,
        amount_per_period: 50,
        interval_days: 7,
        total_periods: 12
      })
      alert('DCA Bot started successfully!')
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || 'Failed to start DCA Bot'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleCustomSymbol = () => {
    const trimmed = customSymbol.trim()
    if (trimmed) {
      const upperSymbol = trimmed.toUpperCase()
      setSymbol(upperSymbol)
      const match = upperSymbol.match(/^([A-Z]+)(USDT|USD|BTC|ETH|BNB)$/)
      if (match && match[1] && match[2]) {
        setBaseCurrency(match[1])
        setQuoteCurrency(match[2])
      }
    }
  }

  const convertPrice = (usdPrice: number): number => {
    return currency === 'THB' ? usdPrice * usdToThbRate : usdPrice
  }

  const formatPrice = (usdPrice: number): string => {
    const converted = convertPrice(usdPrice)
    return converted.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }

  const getActionIcon = () => {
    if (!decision) return <Minus />
    switch (decision.action) {
      case 'BUY': return <TrendingUp className="text-success" />
      case 'SELL': return <TrendingDown className="text-error" />
      case 'HALT': return <AlertTriangle className="text-warning" />
      default: return <Minus className="text-secondary" />
    }
  }

  const getActionClass = () => {
    if (!decision) return 'decision-card'
    return `decision-card decision-${decision.action.toLowerCase()}`
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>AI Trading Dashboard</h1>
        <div className="header-controls">
          <select
            value={currency}
            onChange={(e) => setCurrency(e.target.value as 'USD' | 'THB')}
            className="select"
          >
            <option value="USD">USD</option>
            <option value="THB">THB (฿{usdToThbRate.toFixed(2)}/USD)</option>
          </select>
          <button onClick={fetchData} disabled={loading} className="btn btn-primary">
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Crypto Pair Selector */}
      <div className="card">
        <h3>Select Trading Pair</h3>
        <div className="pair-selector">
          <div className="form-group">
            <label>Base Currency</label>
            <select
              value={baseCurrency}
              onChange={(e) => setBaseCurrency(e.target.value)}
              className="select"
            >
              {popularCryptos.map(crypto => (
                <option key={crypto} value={crypto}>{crypto}</option>
              ))}
            </select>
          </div>

          <div className="pair-separator">/</div>

          <div className="form-group">
            <label>Quote Currency</label>
            <select
              value={quoteCurrency}
              onChange={(e) => setQuoteCurrency(e.target.value)}
              className="select"
            >
              {quoteOptions.map(quote => (
                <option key={quote} value={quote}>{quote}</option>
              ))}
            </select>
          </div>

          <div className="current-pair">
            <strong>Trading Pair:</strong> {symbol}
          </div>
        </div>

        <div className="manual-input">
          <label>Or Enter Custom Symbol:</label>
          <div className="input-group">
            <input
              type="text"
              value={customSymbol}
              onChange={(e) => setCustomSymbol(e.target.value.toUpperCase())}
              placeholder="e.g., BTCUSDT, ETHBNB"
              className="input"
            />
            <button onClick={handleCustomSymbol} className="btn btn-secondary">
              Load
            </button>
          </div>
        </div>
      </div>

      {/* Account Balances */}
      {Object.keys(balances).length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3><Wallet size={20} /> Account Balances</h3>
          </div>
          
          <div className="total-balance-display">
            <span className="total-label">Total Portfolio Value:</span>
            <span className="total-value">
              {currency === 'THB' ? '฿' : '$'}
              {totalPortfolioValue.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              })}
            </span>
          </div>
          
          <div className="balances-grid">
            {Object.entries(balances).map(([crypto, balance]) => (
              <div key={crypto} className="balance-item">
                <span className="crypto-name">{crypto}</span>
                <span className="balance-amount">{balance.toFixed(8)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-2">
        {/* AI Decision Card */}
        <div className={getActionClass()}>
          <div className="card-header">
            <h3>AI Recommendation</h3>
            {getActionIcon()}
          </div>
          <div className="recommendation-focus">
            <span className="focus-label">Analyzing:</span>
            <span className="focus-currency">{baseCurrency}/USDT</span>
          </div>
          
          {decision ? (
            <>
              <div className="decision-action">
                <span className="action-label">Action:</span>
                <span className={`action-value action-${decision.action.toLowerCase()}`}>
                  {decision.action}
                </span>
              </div>
              
              <div className="decision-principle">
                <strong>Principle:</strong>
                <p>{decision.principle}</p>
              </div>
              
              <div className="decision-metrics">
                <div className="metric">
                  <span>Predicted P/L</span>
                  <strong className={decision.predicted_pl_percent >= 0 ? 'text-success' : 'text-error'}>
                    {decision.predicted_pl_percent >= 0 ? '+' : ''}
                    {decision.predicted_pl_percent}%
                  </strong>
                </div>
                <div className="metric">
                  <span>Confidence</span>
                  <strong>{(decision.confidence * 100).toFixed(0)}%</strong>
                </div>
              </div>
              
              <div className="scores-grid">
                {['market', 'sentiment', 'whale', 'fundamental'].map(scoreType => (
                  <div key={scoreType} className="score-item">
                    <span>{scoreType.charAt(0).toUpperCase() + scoreType.slice(1)}</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{width: `${decision.scores[scoreType as keyof typeof decision.scores] * 100}%`}} />
                    </div>
                    <strong>{(decision.scores[scoreType as keyof typeof decision.scores] * 100).toFixed(0)}%</strong>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="loading-state">Loading AI analysis...</div>
          )}
        </div>

        {/* Market Data Card */}
        <div className="card">
          <div className="card-header">
            <h3>Market Data</h3>
            <span className="text-secondary">{symbol}</span>
          </div>
          
          {marketData ? (
            <>
              <div className="price-display">
                <span className="price-label">Current Price</span>
                <span className="price-value">
                  {currency === 'THB' ? '฿' : '$'}
                  {marketData.price ? formatPrice(marketData.price) : 'N/A'}
                </span>
                <span className={`price-change ${(marketData.change_24h || 0) >= 0 ? 'positive' : 'negative'}`}>
                  {(marketData.change_24h || 0) >= 0 ? '+' : ''}
                  {(marketData.change_24h || 0).toFixed(2)}%
                </span>
              </div>
              
              <div className="market-stats">
                <div className="stat">
                  <span>24h High</span>
                  <strong>
                    {currency === 'THB' ? '฿' : '$'}
                    {marketData.high_24h ? formatPrice(marketData.high_24h) : 'N/A'}
                  </strong>
                </div>
                <div className="stat">
                  <span>24h Low</span>
                  <strong>
                    {currency === 'THB' ? '฿' : '$'}
                    {marketData.low_24h ? formatPrice(marketData.low_24h) : 'N/A'}
                  </strong>
                </div>
                <div className="stat">
                  <span>24h Volume</span>
                  <strong>{((marketData.volume_24h || 0) / 1000000).toFixed(2)}M</strong>
                </div>
              </div>
            </>
          ) : (
            <div className="loading-state">Loading market data...</div>
          )}
        </div>
      </div>

      {/* Trading Controls */}
      <div className="card">
        <h3>Manual Trading</h3>
        <div className="trading-controls">
          <div className="form-group">
            <label>Amount ({baseCurrency})</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value))}
              step="0.001"
              min="0.001"
              className="input"
            />
            {balances[baseCurrency] && (
              <span className="help-text">
                Available: {balances[baseCurrency].toFixed(8)} {baseCurrency}
              </span>
            )}
          </div>
          
          <div className="button-group">
            <button
              onClick={() => handleTrade('BUY')}
              disabled={loading || !marketData}
              className="btn btn-success"
            >
              Buy {baseCurrency}
            </button>
            <button
              onClick={() => handleTrade('SELL')}
              disabled={loading || !marketData}
              className="btn btn-error"
            >
              Sell {baseCurrency}
            </button>
          </div>
        </div>
      </div>

      {/* Bot Controls */}
      <div className="grid grid-2">
        <div className="card">
          <h3>Grid Bot</h3>
          <p className="text-secondary">Automated grid trading with 25 levels, 5% range</p>
          <button
            onClick={handleGridBot}
            disabled={loading || !marketData}
            className="btn btn-primary btn-full"
          >
            Start Grid Bot
          </button>
        </div>
        
        <div className="card">
          <h3>DCA Bot</h3>
          <p className="text-secondary">Auto-buy $50 every 7 days (12 periods)</p>
          <button
            onClick={handleDCABot}
            disabled={loading}
            className="btn btn-primary btn-full"
          >
            Start DCA Bot
          </button>
        </div>
      </div>

      {/* AI Force Trading Bot */}
      <div className="card ai-force-bot-card">
        <div className="card-header">
          <h3>🤖 AI Force Trading Bot</h3>
          <div className="bot-header-controls">
            <span className="bot-currency-display">
              Currency: <strong>{aiForceCurrency === 'THB' ? '฿ THB' : '$ USD'}</strong>
            </span>
            <button 
              onClick={() => setShowAIForceSettings(!showAIForceSettings)}
              className="btn btn-secondary btn-sm"
            >
              <Settings size={16} />
              AI Setting
            </button>
          </div>
        </div>
        
        {showAIForceSettings && (
          <div className="ai-force-settings">
            <h4>AI Force Bot Settings</h4>
            
            <div className="settings-grid">
              <div className="form-group">
                <label>Currency for AI Bot</label>
                <select
                  value={aiForceCurrency}
                  onChange={(e) => setAiForceCurrency(e.target.value as 'USD' | 'THB')}
                  className="select"
                >
                  <option value="USD">USD ($)</option>
                  <option value="THB">THB (฿) - Exchange Rate ฿{usdToThbRate.toFixed(2)}/USD</option>
                </select>
                <span className="help-text">Select currency for bot calculations and trading</span>
              </div>

              <div className="form-group">
                <label>
                  <DollarSign size={16} />
                  Trade Volume ({aiForceCurrency})
                </label>
                <input
                  type="number"
                  value={aiForceVolume}
                  onChange={(e) => setAiForceVolume(Math.max(300, parseFloat(e.target.value)))}
                  min={300}
                  step={100}
                  className="input"
                />
                <span className="help-text">
                  Minimum 300 {aiForceCurrency}
                  {aiForceCurrency === 'THB' && ` (≈ $${(aiForceVolume / usdToThbRate).toFixed(2)} USD)`}
                  {aiForceCurrency === 'USD' && ` (≈ ฿${(aiForceVolume * usdToThbRate).toFixed(2)} THB)`}
                </span>
              </div>

              <div className="form-group">
                <label>
                  <TrendingUp size={16} />
                  Max Profit per Day (%)
                </label>
                <input
                  type="number"
                  value={aiForceMaxProfit}
                  onChange={(e) => setAiForceMaxProfit(parseFloat(e.target.value))}
                  min={0.01}
                  max={100}
                  step={0.01}
                  className="input"
                />
                <span className="help-text text-success">
                  Stop when profit ≈ {aiForceCurrency === 'THB' ? '฿' : '$'}{calculateEstimatedProfit().toFixed(2)} {aiForceCurrency}
                </span>
              </div>

              <div className="form-group">
                <label>
                  <TrendingDown size={16} />
                  Max Loss per Day (%)
                </label>
                <input
                  type="number"
                  value={aiForceMaxLoss}
                  onChange={(e) => setAiForceMaxLoss(parseFloat(e.target.value))}
                  min={0.01}
                  max={100}
                  step={0.01}
                  className="input"
                />
                <span className="help-text text-error">
                  Stop when loss ≈ {aiForceCurrency === 'THB' ? '฿' : '$'}{calculateEstimatedLoss().toFixed(2)} {aiForceCurrency}
                </span>
              </div>

              <div className="form-group">
                <label>Minimum Confidence (%)</label>
                <input
                  type="number"
                  value={aiForceMinConfidence}
                  onChange={(e) => setAiForceMinConfidence(parseInt(e.target.value))}
                  min={50}
                  max={100}
                  step={5}
                  className="input"
                />
                <span className="help-text">Trade only when AI confidence ≥ {aiForceMinConfidence}%</span>
              </div>
            </div>

            <div className="fee-info">
              <h5>Binance Thailand Fees</h5>
              <div className="fee-details">
                <div className="fee-item">
                  <span>Maker Fee:</span>
                  <strong>0.1%</strong>
                </div>
                <div className="fee-item">
                  <span>Taker Fee:</span>
                  <strong>0.1%</strong>
                </div>
                <div className="fee-item">
                  <span>Total per Round (Buy+Sell):</span>
                  <strong className="text-warning">0.2%</strong>
                </div>
                <div className="fee-item">
                  <span>Fee per Round:</span>
                  <strong className="text-warning">
                    ≈ {aiForceCurrency === 'THB' ? '฿' : '$'}
                    {aiForceCurrency === 'THB' 
                      ? (aiForceVolume * (BINANCE_FEE_PERCENT / 100)).toFixed(2)
                      : ((aiForceVolume / usdToThbRate) * (BINANCE_FEE_PERCENT / 100)).toFixed(2)
                    } {aiForceCurrency}
                  </strong>
                </div>
              </div>
            </div>
          </div>
        )}

        {aiForceBotStatus && (
          <div className={`bot-status ${aiForceBotStatus.is_running ? 'running' : 'stopped'}`}>
            <div className="status-header">
              <span className={`status-indicator ${aiForceBotStatus.is_running ? 'active' : ''}`}></span>
              <strong>{aiForceBotStatus.is_running ? '🟢 AI Working' : '⚫ AI Stopped'}</strong>
            </div>

            {aiForceBotStatus.is_running && (
              <>
                <div className="status-grid">
                  <div className="status-item">
                    <span>Currency:</span>
                    <strong>{aiForceBotStatus.symbol}</strong>
                  </div>
                  <div className="status-item">
                    <span>Today Rounds:</span>
                    <strong>{aiForceBotStatus.daily_trades} rounds</strong>
                  </div>
                  <div className="status-item">
                    <span>Start Balance:</span>
                    <strong>{aiForceBotStatus.start_balance.toFixed(2)} USDT</strong>
                  </div>
                  <div className="status-item">
                    <span>Current Balance:</span>
                    <strong>{aiForceBotStatus.current_balance.toFixed(2)} USDT</strong>
                  </div>
                </div>

                <div className="profit-display">
                  <span>Today: Profit/Loss:</span>
                  <strong className={aiForceBotStatus.profit_percent >= 0 ? 'text-success' : 'text-error'}>
                    {aiForceBotStatus.profit_percent >= 0 ? '+' : ''}
                    {aiForceBotStatus.profit_percent.toFixed(2)}% 
                    ({aiForceBotStatus.profit_percent >= 0 ? '+' : ''}
                    ${aiForceBotStatus.profit_loss.toFixed(2)})
                  </strong>
                </div>

                {aiForceBotStatus.position_side && (
                  <div className="position-info">
                    <span>Current Position:</span>
                    <strong className={aiForceBotStatus.position_side === 'BUY' ? 'text-success' : 'text-error'}>
                      {aiForceBotStatus.position_side} @ ${aiForceBotStatus.entry_price?.toFixed(2)}
                    </strong>
                  </div>
                )}

                <div className="limit-progress">
                  <div className="progress-item">
                    <label>Profit Progress: {aiForceBotStatus.profit_percent.toFixed(2)}% / {aiForceBotStatus.max_profit}%</label>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill success" 
                        style={{width: `${Math.min(100, (aiForceBotStatus.profit_percent / aiForceBotStatus.max_profit) * 100)}%`}}
                      />
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        <div className="bot-controls">
          {!aiForceBotStatus?.is_running ? (
            <button
              onClick={handleStartAIForceBot}
              disabled={aiForceBotLoading || !marketData}
              className="btn btn-success btn-lg btn-full"
            >
              <Power size={20} />
              Power ON! AI Force Trading Bot
            </button>
          ) : (
            <button
              onClick={handleStopAIForceBot}
              disabled={aiForceBotLoading}
              className="btn btn-error btn-lg btn-full"
            >
              <Power size={20} />
              Stop! AI Force Trading Bot
            </button>
          )}
        </div>

        <p className="bot-description">
          🤖 AI Bot is analyzing <strong>{baseCurrency}/USDT</strong> with currency <strong>{aiForceCurrency === 'THB' ? 'THB (฿)' : 'USD ($)'}</strong>
          <br />
          The bot will trade automatically based on AI signals and calculate Binance's 0.2% fee per round
        </p>
      </div>
       {/* Advanced AI Analysis */}
      <AdvancedAnalysis symbol={symbol} currency={currency} />

      {/* Chart */}
      {marketData && marketData.ohlcv && marketData.ohlcv.length > 0 && (
        <Chart data={marketData.ohlcv} symbol={symbol} />
      )}
    </div>
  )
}