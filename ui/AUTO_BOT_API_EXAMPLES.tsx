/**
 * Auto Bot API Usage Examples
 * 
 * This file demonstrates how to use the Auto Bot API endpoints
 * from the frontend React components.
 */

import apiClient, { AutoBotConfig, AutoBotStatus } from './src/lib/api'
import { useState, useEffect } from 'react'

// ============================================================================
// Example 1: Create and Start Auto Bot
// ============================================================================

export function CreateAndStartBot() {
  const [configId, setConfigId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCreateAndStart = async () => {
    setLoading(true)
    setError(null)

    try {
      // Step 1: Create configuration
      const config: AutoBotConfig = {
        name: 'My First Auto Bot',
        symbol: 'BTC/USDT',
        budget: 10000,
        risk_level: 'moderate',
        min_confidence: 0.7,
        position_size_ratio: 0.95,
        max_daily_loss: 5.0
      }

      const createResponse = await apiClient.createAutoBotConfig(config)
      const newConfigId = createResponse.data.config_id
      setConfigId(newConfigId)

      // Step 2: Start the bot
      await apiClient.startAutoBot(newConfigId)

      console.log('✅ Bot created and started successfully!')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create/start bot')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return { configId, loading, error, handleCreateAndStart }
}

// ============================================================================
// Example 2: Monitor Bot Status (Real-time)
// ============================================================================

export function useAutoBotStatus() {
  const [status, setStatus] = useState<AutoBotStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Poll status every 5 seconds
    const fetchStatus = async () => {
      try {
        const response = await apiClient.getAutoBotStatus()
        setStatus(response.data)
      } catch (err) {
        console.error('Failed to fetch bot status:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)

    return () => clearInterval(interval)
  }, [])

  return { status, loading }
}

// ============================================================================
// Example 3: Display AI Module Health
// ============================================================================

export function AIModuleHealth() {
  const { status } = useAutoBotStatus()

  if (!status || !status.is_running) {
    return <div>Bot is not running</div>
  }

  const modules = [
    { name: 'Brain', value: status.ai_modules.brain, icon: '🧠' },
    { name: 'Decision', value: status.ai_modules.decision, icon: '🎯' },
    { name: 'ML', value: status.ai_modules.ml, icon: '🤖' },
    { name: 'Network', value: status.ai_modules.network, icon: '🌐' },
    { name: 'NLP', value: status.ai_modules.nlp, icon: '💬' },
    { name: 'Perception', value: status.ai_modules.perception, icon: '👁️' },
    { name: 'Learning', value: status.ai_modules.learning, icon: '📚' }
  ]

  return (
    <div className="ai-modules">
      {modules.map(module => (
        <div key={module.name} className="module">
          <span>{module.icon}</span>
          <span>{module.name}</span>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ 
                width: `${module.value}%`,
                backgroundColor: module.value >= 90 ? '#10b981' : module.value >= 70 ? '#f59e0b' : '#ef4444'
              }}
            />
          </div>
          <span>{module.value}%</span>
        </div>
      ))}
    </div>
  )
}

// ============================================================================
// Example 4: Stop Bot
// ============================================================================

export function StopBot() {
  const [stopping, setStopping] = useState(false)

  const handleStop = async (configId: number) => {
    setStopping(true)

    try {
      await apiClient.stopAutoBot(configId)
      console.log('✅ Bot stopped successfully!')
    } catch (err: any) {
      console.error('Failed to stop bot:', err)
      alert(err.response?.data?.detail || 'Failed to stop bot')
    } finally {
      setStopping(false)
    }
  }

  return { handleStop, stopping }
}

// ============================================================================
// Example 5: Get Performance Metrics
// ============================================================================

export function useAutoBotPerformance() {
  const [performance, setPerformance] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPerformance = async () => {
      try {
        const response = await apiClient.getAutoBotPerformance()
        setPerformance(response.data)
      } catch (err) {
        console.error('Failed to fetch performance:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPerformance()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchPerformance, 30000)

    return () => clearInterval(interval)
  }, [])

  return { performance, loading }
}

// ============================================================================
// Example 6: Complete Bot Control Component
// ============================================================================

export function AutoBotController() {
  const { status } = useAutoBotStatus()
  const { performance } = useAutoBotPerformance()
  const { handleStop, stopping } = StopBot()
  const [configId] = useState(1) // From your bot config

  return (
    <div className="auto-bot-controller">
      {/* Status Display */}
      <div className="status-section">
        <h3>Bot Status</h3>
        <div className={`status-badge ${status?.is_running ? 'running' : 'stopped'}`}>
          {status?.is_running ? '🟢 Running' : '🔴 Stopped'}
        </div>
        {status?.is_running && (
          <>
            <p>Symbol: {status.symbol}</p>
            <p>Budget: ${status.budget?.toLocaleString()}</p>
            <p>Last Check: {status.last_check ? new Date(status.last_check).toLocaleString() : 'N/A'}</p>
          </>
        )}
      </div>

      {/* AI Modules */}
      {status?.is_running && <AIModuleHealth />}

      {/* Performance */}
      {performance && (
        <div className="performance-section">
          <h3>Performance</h3>
          <p className={performance.total_pnl >= 0 ? 'profit' : 'loss'}>
            PnL: ${performance.total_pnl.toFixed(2)}
          </p>
          <p>Total Trades: {performance.total_trades}</p>
        </div>
      )}

      {/* Controls */}
      <div className="controls">
        {status?.is_running && (
          <button 
            onClick={() => handleStop(configId)} 
            disabled={stopping}
            className="btn-danger"
          >
            {stopping ? 'Stopping...' : 'Stop Bot'}
          </button>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// Example 7: Error Handling
// ============================================================================

export async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  onError?: (error: any) => void
): Promise<T | null> {
  try {
    return await apiCall()
  } catch (error: any) {
    const message = error.response?.data?.detail || error.message || 'Unknown error'
    console.error('API Error:', message)
    onError?.(error)
    return null
  }
}

// Usage example:
// const status = await safeApiCall(
//   () => apiClient.getAutoBotStatus(),
//   (err) => toast.error('Failed to fetch bot status')
// )

console.log('✅ Auto Bot API usage examples loaded')
