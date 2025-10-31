import { useState, useEffect } from 'react'
import { Brain, TrendingUp, TrendingDown, MessageCircle, Shield, Activity, AlertCircle } from 'lucide-react'
import apiClient, { AdvancedAnalysis as AdvancedAnalysisType } from '../lib/api'

interface Props {
  symbol: string
  currency: string
}

export default function AdvancedAnalysis({ symbol, currency }: Props) {
  const [analysis, setAnalysis] = useState<AdvancedAnalysisType | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAnalysis()
    const interval = setInterval(fetchAnalysis, 60000) // Update every 60 seconds
    return () => clearInterval(interval)
  }, [symbol, currency])

  const fetchAnalysis = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.getAdvancedAnalysis(symbol, currency)
      setAnalysis(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch advanced analysis')
      console.error('Advanced analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'BUY': return 'text-success'
      case 'SELL': return 'text-error'
      case 'HALT': return 'text-warning'
      default: return 'text-secondary'
    }
  }

  const getActionBgColor = (action: string) => {
    switch (action) {
      case 'BUY': return 'bg-success'
      case 'SELL': return 'bg-error'
      case 'HALT': return 'bg-warning'
      default: return 'bg-secondary'
    }
  }

  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case 'TRENDING_UP': return 'text-success'
      case 'TRENDING_DOWN': return 'text-error'
      case 'SIDEWAYS': return 'text-primary'
      default: return 'text-secondary'
    }
  }

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-success'
    if (score < -0.3) return 'text-error'
    return 'text-secondary'
  }

  if (loading && !analysis) {
    return (
      <div className="card advanced-analysis-card">
        <div className="card-header">
          <h3><Brain size={20} /> Advanced AI Analysis</h3>
        </div>
        <div className="loading-state">
          <Activity className="animate-spin" size={32} />
          <p>Analyzing market with AI...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card advanced-analysis-card">
        <div className="card-header">
          <h3><Brain size={20} /> Advanced AI Analysis</h3>
        </div>
        <div className="alert alert-error">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      </div>
    )
  }

  if (!analysis) return null

  return (
    <div className="card advanced-analysis-card">
      {/* Header */}
      <div className="card-header">
        <h3><Brain size={20} /> Advanced AI Analysis</h3>
        <button onClick={fetchAnalysis} disabled={loading} className="btn btn-secondary btn-sm">
          {loading ? 'Analyzing...' : 'Refresh'}
        </button>
      </div>

      {/* Main Decision */}
      <div className={`ai-decision-banner ${getActionBgColor(analysis.action)}`}>
        <div className="decision-content">
          <span className="decision-label">AI Recommendation</span>
          <span className={`decision-action ${getActionColor(analysis.action)}`}>
            {analysis.action}
          </span>
          <span className="decision-confidence">
            Confidence: {(analysis.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="decision-reason">
          <span>{analysis.reason}</span>
        </div>
      </div>

      {/* Risk Levels */}
      <div className="risk-levels-display">
        <div className="risk-level-item">
          <span className="label">Entry Price:</span>
          <strong>${analysis.current_price.toFixed(2)}</strong>
        </div>
        <div className="risk-level-item text-error">
          <span className="label">Stop Loss:</span>
          <strong>${analysis.stop_loss.toFixed(2)} ({analysis.modules.risk_levels.stop_loss_pct.toFixed(2)}%)</strong>
        </div>
        <div className="risk-level-item text-success">
          <span className="label">Take Profit:</span>
          <strong>${analysis.take_profit.toFixed(2)} ({analysis.modules.risk_levels.take_profit_pct.toFixed(2)}%)</strong>
        </div>
        <div className="risk-level-item">
          <span className="label">Risk:Reward:</span>
          <strong>1:{analysis.risk_reward_ratio.toFixed(2)}</strong>
        </div>
      </div>

      {/* 4 Modules Grid */}
      <div className="modules-grid">
        {/* Module 1: Market Regime */}
        <div className="module-card regime-module">
          <div className="module-header">
            <Activity size={18} />
            <h4>Market Regime</h4>
          </div>
          <div className="module-content">
            <div className="regime-display">
              <span className="regime-label">Current State:</span>
              <span className={`regime-value ${getRegimeColor(analysis.modules.regime.regime)}`}>
                {analysis.modules.regime.regime.replace('_', ' ')}
              </span>
            </div>
            <div className="module-metrics">
              <div className="metric-item">
                <span>ADX:</span>
                <strong>{analysis.modules.regime.adx.toFixed(1)}</strong>
              </div>
              <div className="metric-item">
                <span>BB Width:</span>
                <strong>{analysis.modules.regime.bb_width.toFixed(3)}</strong>
              </div>
              <div className="metric-item">
                <span>Confidence:</span>
                <strong>{(analysis.modules.regime.confidence * 100).toFixed(0)}%</strong>
              </div>
            </div>
            <div className={`regime-status ${analysis.modules.regime.allow_mean_reversion ? 'status-active' : 'status-inactive'}`}>
              {analysis.modules.regime.allow_mean_reversion ? '✅ Mean Reversion Enabled' : '🛑 Mean Reversion Disabled'}
            </div>
          </div>
        </div>

        {/* Module 2: Sentiment Analysis */}
        <div className="module-card sentiment-module">
          <div className="module-header">
            <MessageCircle size={18} />
            <h4>Sentiment Analysis</h4>
          </div>
          <div className="module-content">
            <div className="sentiment-display">
              <span className="sentiment-label">Market Sentiment:</span>
              <span className={`sentiment-value ${getSentimentColor(analysis.modules.sentiment.score)}`}>
                {analysis.modules.sentiment.interpretation.replace('_', ' ')}
              </span>
            </div>
            <div className="sentiment-score-bar">
              <div className="score-bar-track">
                <div 
                  className={`score-bar-fill ${analysis.modules.sentiment.score >= 0 ? 'positive' : 'negative'}`}
                  style={{
                    width: `${Math.abs(analysis.modules.sentiment.score) * 100}%`,
                    marginLeft: analysis.modules.sentiment.score < 0 ? 'auto' : '0'
                  }}
                />
              </div>
              <span className="score-value">{analysis.modules.sentiment.score.toFixed(2)}</span>
            </div>
            <div className="module-metrics">
              <div className="metric-item">
                <span>Twitter:</span>
                <strong className={getSentimentColor(analysis.modules.sentiment.twitter)}>
                  {analysis.modules.sentiment.twitter.toFixed(2)}
                </strong>
              </div>
              <div className="metric-item">
                <span>News:</span>
                <strong className={getSentimentColor(analysis.modules.sentiment.news)}>
                  {analysis.modules.sentiment.news.toFixed(2)}
                </strong>
              </div>
            </div>
            <div className={`sentiment-status ${analysis.modules.sentiment.should_trade ? 'status-active' : 'status-inactive'}`}>
              {analysis.modules.sentiment.should_trade ? '✅ Safe to Trade' : '🛑 Avoid Trading'}
            </div>
          </div>
        </div>

        {/* Module 3: Dynamic Risk Management */}
        <div className="module-card risk-module">
          <div className="module-header">
            <Shield size={18} />
            <h4>Dynamic Risk</h4>
          </div>
          <div className="module-content">
            <div className="module-metrics">
              <div className="metric-item">
                <span>ATR:</span>
                <strong>${analysis.modules.risk_levels.atr.toFixed(2)}</strong>
              </div>
              <div className="metric-item">
                <span>Volatility:</span>
                <strong>{(analysis.modules.risk_levels.volatility * 100).toFixed(2)}%</strong>
              </div>
              <div className="metric-item">
                <span>Stop Loss:</span>
                <strong className="text-error">{analysis.modules.risk_levels.stop_loss_pct.toFixed(2)}%</strong>
              </div>
              <div className="metric-item">
                <span>Take Profit:</span>
                <strong className="text-success">{analysis.modules.risk_levels.take_profit_pct.toFixed(2)}%</strong>
              </div>
            </div>
            <div className="risk-visualization">
              <div className="risk-bar">
                <div className="risk-bar-stop" style={{width: '33%'}}>
                  <span>SL</span>
                </div>
                <div className="risk-bar-entry" style={{width: '34%'}}>
                  <span>Entry</span>
                </div>
                <div className="risk-bar-profit" style={{width: '33%'}}>
                  <span>TP</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Module 4: Pattern Recognition */}
        <div className="module-card pattern-module">
          <div className="module-header">
            <TrendingUp size={18} />
            <h4>Pattern Recognition</h4>
          </div>
          <div className="module-content">
            <div className="pattern-signals">
              {analysis.modules.reversal.is_bullish_reversal && (
                <div className="pattern-signal bullish">
                  <TrendingUp size={16} />
                  <span>Bullish Reversal</span>
                </div>
              )}
              {analysis.modules.reversal.is_bearish_reversal && (
                <div className="pattern-signal bearish">
                  <TrendingDown size={16} />
                  <span>Bearish Reversal</span>
                </div>
              )}
              {!analysis.modules.reversal.is_bullish_reversal && !analysis.modules.reversal.is_bearish_reversal && (
                <div className="pattern-signal neutral">
                  <span>No Clear Pattern</span>
                </div>
              )}
            </div>
            <div className="module-metrics">
              <div className="metric-item">
                <span>Confidence:</span>
                <strong>{(analysis.modules.reversal.confidence * 100).toFixed(0)}%</strong>
              </div>
              <div className="metric-item">
                <span>Order Book:</span>
                <strong className={analysis.modules.reversal.order_book_imbalance >= 0 ? 'text-success' : 'text-error'}>
                  {analysis.modules.reversal.order_book_imbalance.toFixed(2)}
                </strong>
              </div>
            </div>
            {analysis.modules.reversal.patterns_detected.length > 0 && (
              <div className="patterns-detected">
                <span className="patterns-label">Patterns:</span>
                <div className="patterns-list">
                  {analysis.modules.reversal.patterns_detected.map((pattern, idx) => (
                    <span key={idx} className="pattern-badge">
                      {pattern.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
