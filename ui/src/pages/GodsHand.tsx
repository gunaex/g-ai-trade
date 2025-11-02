import { useState, useEffect } from 'react'
import { Power, Brain, Zap, AlertCircle, Settings as SettingsIcon } from 'lucide-react'
import AIStatusMonitor from '../components/AIStatusMonitor'
import AutoBotConfig from '../components/AutoBotConfig'
import apiClient, { AutoBotStatus, AutoBotConfig as AutoBotConfigType } from '../lib/api'
import '../styles/gods-hand.css'

// Use shared API types
type BotStatus = AutoBotStatus
type BotConfig = AutoBotConfigType & { id: number; is_active?: boolean }

export default function GodsHand() {
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null)
  const [botConfig, setBotConfig] = useState<BotConfig | null>(null)
  const [loading, setLoading] = useState(false)
  const [showConfig, setShowConfig] = useState(false)

  // Fetch bot status (Real-time polling)
  useEffect(() => {
    fetchBotStatus()
    
    const interval = setInterval(() => {
      fetchBotStatus()
    }, 3000) // Update every 3 seconds
    
    return () => clearInterval(interval)
  }, [])

  const fetchBotStatus = async () => {
    try {
      const response = await apiClient.getAutoBotStatus()
      setBotStatus(response.data)
    } catch (error) {
      console.error('Failed to fetch bot status:', error)
    }
  }

  const handleStartBot = async () => {
    try {
      setLoading(true)
      
      // Create config if not exists
      if (!botConfig) {
        const configPayload: AutoBotConfigType = {
          name: "God's Hand Bot",
          symbol: 'BTC/USDT',
          budget: 10000,
          risk_level: 'moderate',
          min_confidence: 0.7,
          position_size_ratio: 0.95,
          max_daily_loss: 5.0,
        }
        const configResponse = await apiClient.createAutoBotConfig(configPayload)
        const configId = (configResponse.data as any).config_id as number

        if (configId) {
          // Remember created config id locally
          setBotConfig({ id: configId, ...configPayload, is_active: true })
          // Start bot
          await apiClient.startAutoBot(configId)
        }
      } else {
        await apiClient.startAutoBot(botConfig.id)
      }
      
      // Refresh status
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
      
      if (botConfig) {
        await apiClient.stopAutoBot(botConfig.id)
      }
      
      await fetchBotStatus()
      
    } catch (error: any) {
      console.error('Failed to stop bot:', error)
      alert(error.response?.data?.detail || 'Failed to stop bot')
    } finally {
      setLoading(false)
    }
  }

  const isRunning = botStatus?.is_running || false

  return (
    <div className="gods-hand-page">
      {/* Header */}
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
          <button 
            className="btn btn--outline"
            onClick={() => setShowConfig(!showConfig)}
          >
            <SettingsIcon size={20} />
            Configure
          </button>
          
          {isRunning ? (
            <button 
              className="btn btn--danger"
              onClick={handleStopBot}
              disabled={loading}
            >
              <Power size={20} />
              Stop Bot
            </button>
          ) : (
            <button 
              className="btn btn--primary btn--glow"
              onClick={handleStartBot}
              disabled={loading}
            >
              <Zap size={20} />
              Activate God's Hand
            </button>
          )}
        </div>
      </div>

      {/* Status Banner */}
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
            <span>Last Check: {new Date(botStatus.last_check!).toLocaleTimeString()}</span>
          </div>
        )}
      </div>

      {/* Config Panel */}
      {showConfig && (
        <AutoBotConfig 
          onClose={() => setShowConfig(false)}
          onSave={(configId) => {
            // Store minimal local config so Stop/Start knows the id
            setBotConfig({
              id: configId,
              name: "God's Hand Bot",
              symbol: 'BTC/USDT',
              budget: 10000,
              risk_level: 'moderate',
              min_confidence: 0.7,
              position_size_ratio: 0.95,
              max_daily_loss: 5.0,
              is_active: true,
            })
            setShowConfig(false)
          }}
        />
      )}

      {/* AI Status Monitor */}
      {botStatus && (
        <AIStatusMonitor 
          modules={botStatus.ai_modules}
          isRunning={isRunning}
        />
      )}

      {/* Current Position */}
      {isRunning && botStatus?.current_position && (
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
              <span className="value">{new Date(botStatus.current_position.entry_time).toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}

      {/* Warning Messages */}
      {!isRunning && (
        <div className="warning-card">
          <AlertCircle size={24} />
          <div>
            <h4>Bot is Inactive</h4>
            <p>Click "Activate God's Hand" to start autonomous trading</p>
          </div>
        </div>
      )}
    </div>
  )
}
