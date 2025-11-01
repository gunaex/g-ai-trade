import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Trade from './pages/Trade'
import Monitoring from './pages/Monitoring'
import Settings from './pages/Settings'
import Backtesting from './pages/Backtesting'

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Trade />} />
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="/backtest" element={<Backtesting />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
