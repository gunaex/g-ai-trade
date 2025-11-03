import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Trade from './pages/Trade'
import Monitoring from './pages/Monitoring'
import Settings from './pages/Settings'
import Backtesting from './pages/Backtesting'
import GodsHand from './pages/GodsHand'
import Login from './pages/Login'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token')
  
  if (!token) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  const isAuthenticated = !!localStorage.getItem('access_token')

  return (
    <Router>
      <div className="app">
        {isAuthenticated && <Navbar />}
        <main className="main-content">
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Trade />
                </ProtectedRoute>
              }
            />
            <Route path="/trade" element={<Navigate to="/" replace />} />
            
            <Route
              path="/monitoring"
              element={
                <ProtectedRoute>
                  <Monitoring />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/backtest"
              element={
                <ProtectedRoute>
                  <Backtesting />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/gods-hand"
              element={
                <ProtectedRoute>
                  <GodsHand />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
        {isAuthenticated && (
          <footer className="app-footer" style={{ padding: '8px 16px', fontSize: 12, color: '#888', textAlign: 'center' }}>
            <small>
              Times shown use server local time.{' '}
              <a href="/TIMEZONE_INFO.md" target="_blank" rel="noreferrer">
                About Timezones
              </a>
            </small>
          </footer>
        )}
      </div>
    </Router>
  )
}

export default App
