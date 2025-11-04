import { useState, useEffect } from 'react'
import { Power, Brain, Zap, AlertCircle, TrendingUp, Settings as SettingsIcon, Activity } from 'lucide-react'
import AIStatusMonitor from '../components/AIStatusMonitor'
import AutoBotConfig from '../components/AutoBotConfig'
import ActivityLog from '../components/ActivityLog'
import PerformanceDashboard from '../components/PerformanceDashboard'
import ConfigDisplay from '../components/ConfigDisplay'
import apiClient, { AutoBotStatus, FeeSummary } from '../lib/api'
import { useToast } from '../hooks/useToast'
import '../styles/gods-hand.css'

export default function GodsHand() {
  const [botStatus, setBotStatus] = useState<AutoBotStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [showConfig, setShowConfig] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'activity' | 'performance'>('overview')
  const { showToast, ToastContainer } = useToast()
  
  // Separate state for activities that NEVER gets cleared
  const [activities, setActivities] = useState<any[]>([])
  const [feeSummary, setFeeSummary] = useState<FeeSummary | null>(null)
  
  const isRunning = botStatus?.is_running || false

  useEffect(() => {
    fetchBotStatus()
    const interval = setInterval(() => {
      fetchBotStatus()
      if (isRunning) {
        fetchFeeSummary()
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const fetchBotStatus = async () => {
    try {
      const response = await apiClient.getAutoBotStatus()
      
      // Update activities separately - only if we have new ones
      const apiActivities = response.data.activity_log || []
      if (apiActivities.length > 0) {
        setActivities(prev => {
          // Only update if different
          if (apiActivities.length !== prev.length) {
            return apiActivities
          }
          // Check if content changed
          if (apiActivities.length > 0 && prev.length > 0) {
            if (apiActivities[0].timestamp !== prev[0]?.timestamp) {
              return apiActivities
            }
          }
          return prev // Keep same reference
        })
      }
      
      // ✅ Preserve config - don't overwrite if we just saved one
      const newConfig = response.data.config
      
      setBotStatus(prev => ({
        ...response.data,
        // Keep existing config if new one is null and we already have one
        config: newConfig || prev?.config || null,
      }))
    } catch (error) {
      console.error('Failed to fetch bot status:', error)
    }
  }

  const fetchFeeSummary = async () => {
    try {
      const response = await apiClient.getFeeSummary()
      setFeeSummary(response.data)
    } catch (e) {
      // ignore when bot not ready
    }
  }

  const handleStartBot = async () => {
    try {
      setLoading(true)
      
      // Try to use existing saved config first
      let configId: number
      
      if (botStatus?.config?.id) {
        // Use the existing config from status (already saved)
        configId = botStatus.config.id
        showToast(`Using saved configuration (ID #${configId}). Starting bot...`, 'info')
      } else {
        // No config exists, create default config
        const configResponse = await apiClient.createAutoBotConfig({
          name: 'God\'s Hand Bot',
          symbol: 'BTC/USDT',
          budget: 10000,
          risk_level: 'moderate',
          min_confidence: 0.7,
          position_size_ratio: 0.95,
          max_daily_loss: 5.0
        })
        configId = (configResponse.data as any).config_id as number
        showToast(`Configuration created (ID #${configId}). Starting bot...`, 'success')
      }
      
      await apiClient.startAutoBot(configId)
      await fetchBotStatus()
    } catch (error: any) {
      console.error('Failed to start bot:', error)
      alert(error.response?.data?.detail || 'Failed to start bot')
    } finally {
      setLoading(false)
    }
  }

  const handleStopBot = async () => {
    try {
      setLoading(true)
      if (botStatus?.config?.id) {
        await apiClient.stopAutoBot(botStatus.config.id)
      }
      await fetchBotStatus()
    } catch (error: any) {
      console.error('Failed to stop bot:', error)
      alert(error.response?.data?.detail || 'Failed to stop bot')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="gods-hand-page">
      <div className="gods-hand-header">
        <div className="header-content">
          <div className="header-icon">
            <Brain size={48} className="icon-glow" />
          </div>
          <div>
            <h1>God's Hand</h1>
            <p>AI-Powered Autonomous Trading System</p>
          </div>
        </div>
        <div className="header-actions">
          <button className="btn btn--outline" onClick={() => setShowConfig(!showConfig)}>
            <SettingsIcon size={20} />
            Configure
          </button>
          {isRunning ? (
            <button className="btn btn--danger" onClick={handleStopBot} disabled={loading}>
              <Power size={20} />
              Stop Bot
            </button>
          ) : (
            <button className="btn btn--primary btn--glow" onClick={handleStartBot} disabled={loading}>
              <Zap size={20} />
              Activate God's Hand
            </button>
          )}
        </div>
      </div>

      <div className={`status-banner ${isRunning ? 'status-active' : 'status-inactive'}`}>
        <div className="status-indicator">
          <div className={`pulse-dot ${isRunning ? 'active' : ''}`} />
          <span>{isRunning ? 'ACTIVE' : 'INACTIVE'}</span>
        </div>
        {isRunning && botStatus && (
          <div className="status-info">
            <span>Symbol: {botStatus.symbol}</span>
            <span>•</span>
            <span>Budget: ${botStatus.budget?.toLocaleString()}</span>
            <span>•</span>
            <span>Last Check: {new Date(botStatus.last_check!).toLocaleTimeString('th-TH', { 
              timeZone: 'Asia/Bangkok',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: false
            })}</span>
          </div>
        )}
      </div>

      {showConfig && (
        <AutoBotConfig 
          initialConfig={botStatus?.config ? {
            name: (botStatus.config as any).name,
            symbol: (botStatus.config as any).symbol,
            budget: (botStatus.config as any).budget,
            risk_level: (botStatus.config as any).risk_level,
            min_confidence: (botStatus.config as any).min_confidence,
            position_size_ratio: (botStatus.config as any).position_size_ratio,
            max_daily_loss: (botStatus.config as any).max_daily_loss,
          } : undefined}
          onClose={() => setShowConfig(false)} 
          onSave={async (configId: number) => {
            try {
              // Fetch and display the saved config immediately
              const configResp = await apiClient.getAutoBotConfig(configId)
              const savedConfig = configResp.data as any
              
              console.log('💾 Saved config received:', savedConfig)
              
              // Update BOTH config AND top-level symbol/budget for consistency
              setBotStatus(prev => ({
                ...(prev || {
                  is_running: false,
                  ai_modules: { brain: 0, decision: 0, ml: 0, network: 0, nlp: 0, perception: 0, learning: 0 },
                  current_position: null,
                  last_check: null,
                }),
                config: savedConfig,
                symbol: savedConfig.symbol,  // ✅ Update status banner symbol
                budget: savedConfig.budget,  // ✅ Update status banner budget
              }))
              
              console.log('✅ Updated botStatus with new config')
              
              showToast(`Configuration saved (ID #${configId}).`, 'success')
              
              // Make sure user sees the card
              setActiveTab('overview')
              setTimeout(() => {
                const el = document.getElementById('config-section')
                if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
              }, 50)
            } catch (e) {
              console.error('Failed to load saved config:', e)
              showToast('Configuration saved, but failed to load details.', 'warning')
            } finally {
              setShowConfig(false)
            }
          }} 
        />
      )}

      <div className="tabs-container">
        <button className={`tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
          <Brain size={18} />
          Overview
        </button>
        <button className={`tab ${activeTab === 'activity' ? 'active' : ''}`} onClick={() => setActiveTab('activity')}>
          <Activity size={18} />
          Activity Log
        </button>
        <button className={`tab ${activeTab === 'performance' ? 'active' : ''}`} onClick={() => setActiveTab('performance')}>
          <TrendingUp size={18} />
          Performance
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && botStatus && (
        <>
          {botStatus.config && (
            <div id="config-section">
              <ConfigDisplay config={botStatus.config as any} />
            </div>
          )}
          <AIStatusMonitor modules={botStatus.ai_modules} isRunning={isRunning} />
          {isRunning && botStatus.fee_settings && (
            <div className="position-card">
              <h3>🛡️ Fee Protection</h3>
              <div className="position-details">
                <div className="detail-item">
                  <span className="label">Profit Threshold:</span>
                  <span className="value">{botStatus.fee_settings.min_profit_multiple.toFixed(1)} × fees</span>
                </div>
                <div className="detail-item">
                  <span className="label">Trade Limits:</span>
                  <span className="value">{botStatus.fee_settings.max_trades_per_hour}/h • {botStatus.fee_settings.max_trades_per_day}/day</span>
                </div>
                <div className="detail-item">
                  <span className="label">Min Hold Time:</span>
                  <span className="value">{botStatus.fee_settings.min_hold_time_minutes} min</span>
                </div>
              </div>
            </div>
          )}
          {isRunning && botStatus.current_position && (
            <div className="position-card">
              <h3>🎯 Current Position</h3>
              <div className="position-details">
                <div className="detail-item">
                  <span className="label">Entry Price:</span>
                  <span className="value">${botStatus.current_position.entry_price.toFixed(2)}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Quantity:</span>
                  <span className="value">{botStatus.current_position.quantity.toFixed(6)}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Entry Time:</span>
                  <span className="value">{new Date(botStatus.current_position.entry_time).toLocaleString('th-TH', {
                    timeZone: 'Asia/Bangkok',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                  })}</span>
                </div>
                {botStatus.breakeven && (
                  <>
                    <div className="detail-item">
                      <span className="label">Breakeven:</span>
                      <span className="value">${botStatus.breakeven.breakeven_price.toFixed(2)} (+{botStatus.breakeven.breakeven_pct.toFixed(2)}%)</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Min Profitable:</span>
                      <span className="value">${botStatus.breakeven.min_profitable_price.toFixed(2)} (+{botStatus.breakeven.min_profitable_pct.toFixed(2)}%)</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Activity Log Tab - Always render to prevent unmount/remount */}
      {activeTab === 'activity' && (
        <ActivityLog 
          key="activity-log-stable"
          activities={activities} 
          isRunning={isRunning} 
        />
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && botStatus && (
        <PerformanceDashboard 
          performance={botStatus.performance ?? {
            total_pnl: 0,
            total_trades: 0,
            win_trades: 0,
            loss_trades: 0,
            win_rate: 0,
            total_fees: 0,
            open_position_value: 0
          }} 
          isRunning={isRunning} 
        />
      )}

      {activeTab === 'performance' && isRunning && (
        <div className="position-card">
          <h3>📊 24h Fee Summary</h3>
          {feeSummary ? (
            <div className="position-details">
              <div className="detail-item">
                <span className="label">Trades (24h):</span>
                <span className="value">{feeSummary.trades_24h} (B{feeSummary.buy_trades_24h} / S{feeSummary.sell_trades_24h})</span>
              </div>
              <div className="detail-item">
                <span className="label">Fees (24h):</span>
                <span className="value">${feeSummary.fees_24h_usd.toFixed(2)}</span>
              </div>
              <div className="detail-item">
                <span className="label">Net Profit (24h):</span>
                <span className="value">${feeSummary.net_profit_24h_usd.toFixed(2)}</span>
              </div>
              <div className="detail-item">
                <span className="label">Fee/Profit Ratio:</span>
                <span className="value">{feeSummary.fee_to_profit_ratio.toFixed(1)}%</span>
              </div>
            </div>
          ) : (
            <p>Loading fee summary...</p>
          )}
        </div>
      )}

      {!isRunning && (
        <div className="warning-card">
          <AlertCircle size={24} />
          <div>
            <h4>Bot is Inactive</h4>
            <p>Click "Activate God's Hand" to start autonomous trading</p>
          </div>
        </div>
      )}
      <ToastContainer />
    </div>
  )
}
