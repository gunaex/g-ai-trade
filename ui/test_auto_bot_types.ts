/**
 * Type checking test for Auto Bot API
 * Run: npx tsc --noEmit test_auto_bot_types.ts
 */

import apiClient, { AutoBotConfig, AutoBotStatus, AutoBotPerformance } from './src/lib/api'

// Test 1: AutoBotConfig interface
const testConfig: AutoBotConfig = {
  name: 'Test Bot',
  symbol: 'BTC/USDT',
  budget: 10000,
  risk_level: 'moderate',
  min_confidence: 0.7,
  position_size_ratio: 0.95,
  max_daily_loss: 5.0
}

// Test 2: AutoBotStatus interface
const testStatus: AutoBotStatus = {
  is_running: true,
  ai_modules: {
    brain: 98,
    decision: 95,
    ml: 92,
    network: 88,
    nlp: 85,
    perception: 90,
    learning: 87
  },
  current_position: {
    trade_id: 123,
    entry_price: 43250.00,
    quantity: 0.1,
    entry_time: '2025-11-02T13:30:00'
  },
  last_check: '2025-11-02T13:35:00',
  symbol: 'BTC/USDT',
  budget: 10000
}

// Test 3: AutoBotPerformance interface
const testPerformance: AutoBotPerformance = {
  total_pnl: 125.50,
  total_trades: 10,
  recent_trades: [
    {
      timestamp: '2025-11-02T13:25:00',
      symbol: 'BTC/USDT',
      side: 'BUY',
      price: 43250.00,
      amount: 0.1
    }
  ]
}

// Test 4: API client methods
async function testApiMethods() {
  // All methods should be typed correctly
  const createResult = await apiClient.createAutoBotConfig(testConfig)
  const config = await apiClient.getAutoBotConfig(1)
  const startResult = await apiClient.startAutoBot(1)
  const stopResult = await apiClient.stopAutoBot(1)
  const status = await apiClient.getAutoBotStatus()
  const performance = await apiClient.getAutoBotPerformance()
  
  console.log('✅ All Auto Bot API methods are properly typed')
}

console.log('✅ TypeScript type checking passed for Auto Bot interfaces')
