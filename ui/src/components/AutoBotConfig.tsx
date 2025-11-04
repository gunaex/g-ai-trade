import { useState } from 'react'
import { X, Save, Info } from 'lucide-react'
import apiClient from '../lib/api'

interface Props {
  onClose: () => void
  onSave: (configId: number) => void
  initialConfig?: {
    name: string
    symbol: string
    budget: number
    paper_trading?: boolean
    risk_level: 'conservative' | 'moderate' | 'aggressive'
    min_confidence: number
    position_size_ratio: number
    max_daily_loss: number
  }
}

export default function AutoBotConfig({ onClose, onSave, initialConfig }: Props) {
  const [config, setConfig] = useState<{
    name: string
    symbol: string
    budget: number
    paper_trading: boolean
    risk_level: 'conservative' | 'moderate' | 'aggressive'
    min_confidence: number
    position_size_ratio: number
    max_daily_loss: number
  }>(() => {
    // Initialize state from initialConfig if provided, otherwise use defaults
    if (initialConfig) {
      return {
        name: initialConfig.name ?? "God's Hand Bot",
        symbol: initialConfig.symbol ?? 'BTC/USDT',
        budget: Number(initialConfig.budget ?? 10000),
        paper_trading: initialConfig.paper_trading ?? true,  // Default to paper trading (safe)
        risk_level: (initialConfig.risk_level ?? 'moderate') as 'conservative' | 'moderate' | 'aggressive',
        min_confidence: Number(initialConfig.min_confidence ?? 0.7),
        position_size_ratio: Number(initialConfig.position_size_ratio ?? 0.95),
        max_daily_loss: Number(initialConfig.max_daily_loss ?? 5.0),
      }
    }
    return {
      name: "God's Hand Bot",
      symbol: 'BTC/USDT',
      budget: 10000,
      paper_trading: true,  // Default to paper trading (safe)
      risk_level: 'moderate',
      min_confidence: 0.7,
      position_size_ratio: 0.95,
      max_daily_loss: 5.0
    }
  })

  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    try {
      setSaving(true)
      
      console.log('💾 Saving config:', config)
      
      const response = await apiClient.createAutoBotConfig(config)
      
      console.log('✅ Config saved, response:', response.data)
      
      // Pass the config_id to parent
      const configId = (response.data as any).config_id as number
      if (configId) {
        console.log('📤 Calling onSave with configId:', configId)
        onSave(configId)
      }
      
    } catch (error: any) {
      console.error('Failed to save config:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to save configuration'
      alert(errorMessage)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="config-modal">
        <div className="modal-header">
          <h2>⚙️ Bot Configuration</h2>
          <button className="btn-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          {/* Bot Name */}
          <div className="form-group">
            <label>Bot Name</label>
            <input 
              type="text"
              value={config.name}
              onChange={(e) => setConfig({...config, name: e.target.value})}
              placeholder="Enter bot name"
            />
          </div>

          {/* Symbol */}
          <div className="form-group">
            <label>Trading Symbol</label>
            <select 
              value={config.symbol}
              onChange={(e) => setConfig({...config, symbol: e.target.value})}
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
            </select>
          </div>

          {/* Budget */}
          <div className="form-group">
            <label>Budget (USD)</label>
            <input 
              type="number"
              value={Number.isFinite(config.budget) ? config.budget : 0}
              onChange={(e) => {
                const v = e.target.value
                setConfig({
                  ...config,
                  budget: v === '' ? 0 : Number.isNaN(parseFloat(v)) ? 0 : parseFloat(v),
                })
              }}
              min={100}
              step={100}
            />
            <span className="form-hint">Total capital allocated to this bot</span>
          </div>

          {/* Paper Trading Toggle */}
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              Trading Mode
              <Info size={16} style={{ color: '#888' }} />
            </label>
            <div className="paper-trading-toggle" style={{
              padding: '12px',
              border: '2px solid',
              borderColor: config.paper_trading ? '#10b981' : '#f59e0b',
              borderRadius: '8px',
              backgroundColor: config.paper_trading ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)'
            }}>
              <label className="radio-label" style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <input 
                  type="checkbox"
                  checked={config.paper_trading}
                  onChange={(e) => setConfig({...config, paper_trading: e.target.checked})}
                  style={{ width: '20px', height: '20px' }}
                />
                <span style={{ fontWeight: 'bold', color: config.paper_trading ? '#10b981' : '#f59e0b' }}>
                  {config.paper_trading ? '📝 Paper Trading (Simulated)' : '💰 Live Trading (Real Money)'}
                </span>
              </label>
              <span className="form-hint" style={{ display: 'block', marginLeft: '32px' }}>
                {config.paper_trading 
                  ? '✅ Safe mode: Test strategies without risking real money' 
                  : '⚠️  CAUTION: Real orders will be placed on Binance TH'}
              </span>
            </div>
          </div>

          {/* Risk Level */}
          <div className="form-group">
            <label>Risk Level</label>
            <div className="radio-group">
              <label className="radio-label">
                <input 
                  type="radio"
                  name="risk"
                  value="conservative"
                  checked={config.risk_level === 'conservative'}
                  onChange={(e) => setConfig({...config, risk_level: e.target.value as 'conservative' | 'moderate' | 'aggressive'})}
                />
                <span>Conservative</span>
              </label>
              
              <label className="radio-label">
                <input 
                  type="radio"
                  name="risk"
                  value="moderate"
                  checked={config.risk_level === 'moderate'}
                  onChange={(e) => setConfig({...config, risk_level: e.target.value as 'conservative' | 'moderate' | 'aggressive'})}
                />
                <span>Moderate</span>
              </label>
              
              <label className="radio-label">
                <input 
                  type="radio"
                  name="risk"
                  value="aggressive"
                  checked={config.risk_level === 'aggressive'}
                  onChange={(e) => setConfig({...config, risk_level: e.target.value as 'conservative' | 'moderate' | 'aggressive'})}
                />
                <span>Aggressive</span>
              </label>
            </div>
          </div>

          {/* Min Confidence */}
          <div className="form-group">
            <label>Minimum AI Confidence (%)</label>
            <input 
              type="range"
              min="50"
              max="95"
              step="5"
              value={config.min_confidence * 100}
              onChange={(e) => setConfig({...config, min_confidence: parseFloat(e.target.value) / 100})}
            />
            <div className="range-value">{(config.min_confidence * 100).toFixed(0)}%</div>
            <span className="form-hint">Bot will only trade when AI confidence is above this threshold</span>
          </div>

          {/* Position Size */}
          <div className="form-group">
            <label>Position Size (%)</label>
            <input 
              type="range"
              min="50"
              max="100"
              step="5"
              value={config.position_size_ratio * 100}
              onChange={(e) => setConfig({...config, position_size_ratio: parseFloat(e.target.value) / 100})}
            />
            <div className="range-value">{(config.position_size_ratio * 100).toFixed(0)}%</div>
            <span className="form-hint">Percentage of budget used per trade</span>
          </div>

          {/* Max Daily Loss */}
          <div className="form-group">
            <label>Max Daily Loss (%)</label>
            <input 
              type="number"
              value={Number.isFinite(config.max_daily_loss) ? config.max_daily_loss : 0}
              onChange={(e) => {
                const v = e.target.value
                setConfig({
                  ...config,
                  max_daily_loss: v === '' ? 0 : Number.isNaN(parseFloat(v)) ? 0 : parseFloat(v),
                })
              }}
              min={1}
              max={20}
              step={0.5}
            />
            <span className="form-hint">Bot will stop if daily loss exceeds this percentage</span>
          </div>

          {/* Info Box */}
          <div className="info-box">
            <Info size={20} />
            <div>
              <strong>Important:</strong> These settings control the bot's trading behavior. 
              Start with conservative settings and adjust based on performance.
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn--outline" onClick={onClose}>
            Cancel
          </button>
          <button 
            className="btn btn--primary"
            onClick={handleSave}
            disabled={saving}
          >
            <Save size={18} />
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </div>
  )
}
