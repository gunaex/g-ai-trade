import { useState, useEffect } from 'react'
import { Power, Brain, Zap, AlertCircle, TrendingUp, Settings as SettingsIcon, Activity } from 'lucide-react'
import AIStatusMonitor from '../components/AIStatusMonitor'
import AutoBotConfig from '../components/AutoBotConfig'
import ActivityLog from '../components/ActivityLog'
import PerformanceDashboard from '../components/PerformanceDashboard'
import ConfigDisplay from '../components/ConfigDisplay'
import apiClient, { AutoBotStatus } from '../lib/api'
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
  
  const isRunning = botStatus?.is_running || false

  useEffect(() => {
    fetchBotStatus()
    const interval = setInterval(() => {
      fetchBotStatus()
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
      
      setBotStatus(prev => ({
        ...response.data,
        config: response.data.config ?? prev?.config,
      }))
    } catch (error) {
      console.error('Failed to fetch bot status:', error)
    }
  }

  const handleStartBot = async () => {
    try {
      setLoading(true)
      const configResponse = await apiClient.createAutoBotConfig({
        name: 'God\'s Hand Bot',
        symbol: 'BTC/USDT',
        budget: 10000,
        risk_level: 'moderate',
        min_confidence: 0.7,
        position_size_ratio: 0.95,
        max_daily_loss: 5.0
      })
      const configId = (configResponse.data as any).config_id as number
      showToast(`Configuration created (ID #${configId}). Starting bot...`, 'success')
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
            <span>Last Check: {new Date(botStatus.last_check!).toLocaleTimeString()}</span>
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
              setBotStatus(prev => ({
                ...(prev || {
                  is_running: false,
                  ai_modules: { brain: 0, decision: 0, ml: 0, network: 0, nlp: 0, perception: 0, learning: 0 },
                  current_position: null,
                  last_check: null,
                }),
                config: configResp.data as any,
              }))
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
                  <span className="value">{new Date(botStatus.current_position.entry_time).toLocaleString()}</span>
                </div>
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
          performance={botStatus.performance} 
          isRunning={isRunning} 
        />
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
