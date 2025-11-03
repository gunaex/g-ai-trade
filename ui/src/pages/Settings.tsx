import { useState, useEffect } from 'react'
import { Key, Shield, Bell, Database, Settings as SettingsIcon } from 'lucide-react'
import api from '../lib/api'

export default function Settings() {
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [hasApiKeys, setHasApiKeys] = useState(false)
  const [apiKeyPreview, setApiKeyPreview] = useState('')
  const [maxDrawdown, setMaxDrawdown] = useState(5)
  const [positionSize, setPositionSize] = useState(2)
  const [correlationLimit, setCorrelationLimit] = useState(0.8)
  const [saved, setSaved] = useState(false)
  const [apiKeySaved, setApiKeySaved] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Fee Protection state
  const [feeSettingsAvailable, setFeeSettingsAvailable] = useState<boolean>(false)
  const [feeLoading, setFeeLoading] = useState(false)
  const [feeError, setFeeError] = useState('')
  const [feeSaved, setFeeSaved] = useState(false)
  const [makerFee, setMakerFee] = useState<number>(0.001)
  const [takerFee, setTakerFee] = useState<number>(0.001)
  const [minProfitMultiple, setMinProfitMultiple] = useState<number>(3.0)
  const [maxTradesPerHour, setMaxTradesPerHour] = useState<number>(2)
  const [maxTradesPerDay, setMaxTradesPerDay] = useState<number>(10)
  const [minHoldTimeMinutes, setMinHoldTimeMinutes] = useState<number>(30)

  // Load API key status on mount
  useEffect(() => {
    loadApiKeyStatus()
    loadFeeSettings()
  }, [])

  const loadApiKeyStatus = async () => {
    try {
      const { data } = await api.getApiKeysStatus()
      setHasApiKeys(data.has_api_keys)
      setApiKeyPreview(data.api_key_preview || '')
    } catch (err: any) {
      console.error('Failed to load API key status:', err)
    }
  }

  const handleSaveApiKeys = async () => {
    if (!apiKey.trim() || !apiSecret.trim()) {
      setError('Both API key and secret are required')
      return
    }

    setLoading(true)
    setError('')

    try {
      await api.saveApiKeys(apiKey, apiSecret)
      
      setApiKeySaved(true)
      setApiKey('')
      setApiSecret('')
      await loadApiKeyStatus()
      
      setTimeout(() => setApiKeySaved(false), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save API keys')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteApiKeys = async () => {
    if (!confirm('Are you sure you want to delete your API keys? This cannot be undone.')) {
      return
    }

    setLoading(true)
    setError('')

    try {
      await api.deleteApiKeys()
      setHasApiKeys(false)
      setApiKeyPreview('')
      setApiKeySaved(true)
      setTimeout(() => setApiKeySaved(false), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete API keys')
    } finally {
      setLoading(false)
    }
  }

  const loadFeeSettings = async () => {
    setFeeLoading(true)
    setFeeError('')
    try {
      const { data } = await api.getFeeSettings()
      setMakerFee(Number(data.maker_fee))
      setTakerFee(Number(data.taker_fee))
      setMinProfitMultiple(Number(data.min_profit_multiple))
      setMaxTradesPerHour(Number(data.max_trades_per_hour))
      setMaxTradesPerDay(Number(data.max_trades_per_day))
      setMinHoldTimeMinutes(Number(data.min_hold_time_minutes))
      setFeeSettingsAvailable(true)
    } catch (err: any) {
      // If bot not running or no fee protection yet
      setFeeSettingsAvailable(false)
      if (err?.response?.data?.detail) {
        setFeeError(err.response.data.detail)
      }
    } finally {
      setFeeLoading(false)
    }
  }

  const handleSaveFeeSettings = async () => {
    setFeeLoading(true)
    setFeeError('')
    setFeeSaved(false)
    try {
      await api.updateFeeSettings({
        maker_fee: makerFee,
        taker_fee: takerFee,
        min_profit_multiple: minProfitMultiple,
        max_trades_per_hour: maxTradesPerHour,
        max_trades_per_day: maxTradesPerDay,
        min_hold_time_minutes: minHoldTimeMinutes,
      })
      setFeeSaved(true)
      setTimeout(() => setFeeSaved(false), 2500)
    } catch (err: any) {
      setFeeError(err?.response?.data?.detail || 'Failed to save fee settings')
    } finally {
      setFeeLoading(false)
    }
  }

  const handleSave = () => {
    // Save other settings to localStorage
    localStorage.setItem('settings', JSON.stringify({
      maxDrawdown,
      positionSize,
      correlationLimit
    }))
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Settings</h1>
      </div>

      {/* API Configuration */}
      <div className="card">
        <div className="card-header">
          <h3><Key size={20} /> API Configuration</h3>
        </div>
        
        <div className="alert alert-warning">
          <Shield size={20} />
          <span>API keys are encrypted using Fernet encryption before storage</span>
        </div>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        {hasApiKeys && (
          <div className="alert alert-success" style={{ marginBottom: '1rem' }}>
            <Shield size={20} />
            <span>API Key configured: {apiKeyPreview}</span>
          </div>
        )}

        <div className="form-group">
          <label>Binance API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder={hasApiKeys ? "Enter new API key to update" : "Enter your Binance API key"}
            className="input"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Binance API Secret</label>
          <input
            type="password"
            value={apiSecret}
            onChange={(e) => setApiSecret(e.target.value)}
            placeholder={hasApiKeys ? "Enter new API secret to update" : "Enter your Binance API secret"}
            className="input"
            disabled={loading}
          />
        </div>

        <div className="button-group">
          <button 
            className="btn btn-primary" 
            onClick={handleSaveApiKeys}
            disabled={loading || (!apiKey && !apiSecret)}
          >
            {loading ? 'Saving...' : (apiKeySaved ? '✓ API Keys Saved!' : (hasApiKeys ? 'Update API Keys' : 'Save & Encrypt API Keys'))}
          </button>
          
          {hasApiKeys && (
            <button 
              className="btn btn-error" 
              onClick={handleDeleteApiKeys}
              disabled={loading}
            >
              Delete API Keys
            </button>
          )}
        </div>
      </div>

      {/* Risk Management */}
      <div className="card">
        <div className="card-header">
          <h3><Shield size={20} /> Risk Management</h3>
        </div>

        <div className="form-group">
          <label>Max Drawdown (%)</label>
          <input
            type="number"
            value={maxDrawdown}
            onChange={(e) => setMaxDrawdown(parseFloat(e.target.value))}
            min="1"
            max="20"
            step="0.5"
            className="input"
          />
          <span className="help-text">Auto-halt trading if loss exceeds this percentage</span>
        </div>

        <div className="form-group">
          <label>Position Size (% per trade)</label>
          <input
            type="number"
            value={positionSize}
            onChange={(e) => setPositionSize(parseFloat(e.target.value))}
            min="0.5"
            max="10"
            step="0.5"
            className="input"
          />
          <span className="help-text">Percentage of portfolio to use per trade</span>
        </div>

        <div className="form-group">
          <label>Correlation Limit</label>
          <input
            type="number"
            value={correlationLimit}
            onChange={(e) => setCorrelationLimit(parseFloat(e.target.value))}
            min="0"
            max="1"
            step="0.1"
            className="input"
          />
          <span className="help-text">Block trades with correlation above this threshold</span>
        </div>
      </div>

      {/* Notifications */}
      <div className="card">
        <div className="card-header">
          <h3><Bell size={20} /> Notifications</h3>
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input type="checkbox" defaultChecked />
            <span>Email notifications for trades</span>
          </label>
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input type="checkbox" defaultChecked />
            <span>Alert on high volatility</span>
          </label>
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input type="checkbox" />
            <span>Daily performance summary</span>
          </label>
        </div>
      </div>

      {/* Fee Protection (God's Hand) */}
      <div className="card">
        <div className="card-header">
          <h3><SettingsIcon size={20} /> Fee Protection</h3>
        </div>

        {!feeSettingsAvailable && (
          <div className="alert alert-warning" style={{ marginBottom: '1rem' }}>
            Start God's Hand to configure fee protection, then refresh this page.
          </div>
        )}

        {feeError && (
          <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
            {feeError}
          </div>
        )}

        <div className="grid-2col">
          <div className="form-group">
            <label>Maker Fee (%)</label>
            <input
              type="number"
              value={(makerFee * 100).toFixed(4)}
              onChange={(e) => setMakerFee(parseFloat(e.target.value) / 100)}
              min="0"
              step="0.01"
              className="input"
              disabled={!feeSettingsAvailable || feeLoading}
            />
            <span className="help-text">Exchange maker fee (e.g., 0.10)</span>
          </div>

          <div className="form-group">
            <label>Taker Fee (%)</label>
            <input
              type="number"
              value={(takerFee * 100).toFixed(4)}
              onChange={(e) => setTakerFee(parseFloat(e.target.value) / 100)}
              min="0"
              step="0.01"
              className="input"
              disabled={!feeSettingsAvailable || feeLoading}
            />
            <span className="help-text">Exchange taker fee (e.g., 0.10)</span>
          </div>
        </div>

        <div className="grid-2col">
          <div className="form-group">
            <label>Min Profit Multiple (× Fees)</label>
            <input
              type="number"
              value={minProfitMultiple}
              onChange={(e) => setMinProfitMultiple(parseFloat(e.target.value))}
              min="1"
              max="10"
              step="0.5"
              className="input"
              disabled={!feeSettingsAvailable || feeLoading}
            />
            <span className="help-text">Profit must exceed fees by this multiple</span>
          </div>

          <div className="form-group">
            <label>Minimum Hold Time (minutes)</label>
            <input
              type="number"
              value={minHoldTimeMinutes}
              onChange={(e) => setMinHoldTimeMinutes(parseInt(e.target.value))}
              min="0"
              max="240"
              step="5"
              className="input"
              disabled={!feeSettingsAvailable || feeLoading}
            />
            <span className="help-text">Prevents quick flips that waste fees</span>
          </div>
        </div>

        <div className="grid-2col">
          <div className="form-group">
            <label>Max Trades per Hour</label>
            <input
              type="number"
              value={maxTradesPerHour}
              onChange={(e) => setMaxTradesPerHour(parseInt(e.target.value))}
              min="0"
              max="20"
              step="1"
              className="input"
              disabled={!feeSettingsAvailable || feeLoading}
            />
            <span className="help-text">Protects against overtrading (hourly)</span>
          </div>

          <div className="form-group">
            <label>Max Trades per Day</label>
            <input
              type="number"
              value={maxTradesPerDay}
              onChange={(e) => setMaxTradesPerDay(parseInt(e.target.value))}
              min="0"
              max="100"
              step="1"
              className="input"
              disabled={!feeSettingsAvailable || feeLoading}
            />
            <span className="help-text">Protects against overtrading (daily)</span>
          </div>
        </div>

        <div className="button-group">
          <button 
            className="btn btn-primary" 
            onClick={handleSaveFeeSettings}
            disabled={!feeSettingsAvailable || feeLoading}
          >
            {feeLoading ? 'Saving...' : (feeSaved ? '✓ Fee Settings Saved!' : 'Save Fee Settings')}
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={loadFeeSettings}
            disabled={feeLoading}
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Database */}
      <div className="card">
        <div className="card-header">
          <h3><Database size={20} /> Data Management</h3>
        </div>

        <div className="button-group">
          <button className="btn btn-secondary">Export Trade History</button>
          <button className="btn btn-secondary">Backup Database</button>
          <button className="btn btn-error">Clear All Data</button>
        </div>
      </div>

      {/* Save Button */}
      <div className="card">
        <button onClick={handleSave} className="btn btn-primary btn-large">
          {saved ? '✓ Settings Saved!' : 'Save All Settings'}
        </button>
      </div>
    </div>
  )
}
