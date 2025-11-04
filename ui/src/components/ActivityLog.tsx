import { useEffect, useRef, memo } from 'react'
import { Clock, CheckCircle, AlertCircle, Info, XCircle } from 'lucide-react'

interface Activity {
  timestamp: string
  message: string
  level: 'info' | 'success' | 'warning' | 'error'
  data?: any
}

interface Props {
  activities: Activity[]
  isRunning: boolean
}

function ActivityLog({ activities, isRunning }: Props) {
  const logEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new activity
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activities.length]) // Only scroll when length changes, not array reference

  const getActivityIcon = (level: string) => {
    switch (level) {
      case 'success':
        return <CheckCircle size={18} className="icon-success" />
      case 'warning':
        return <AlertCircle size={18} className="icon-warning" />
      case 'error':
        return <XCircle size={18} className="icon-error" />
      default:
        return <Info size={18} className="icon-info" />
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    // Convert to Thailand timezone (UTC+7)
    return date.toLocaleTimeString('th-TH', { 
      timeZone: 'Asia/Bangkok',
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false  // 24-hour format
    })
  }

  return (
    <div className="activity-log-container">
      <div className="activity-header">
        <div className="header-left">
          <Clock size={24} />
          <h2>Real-time Activity Log</h2>
        </div>
        <div className="activity-status">
          <div className={`status-dot ${isRunning ? 'active' : 'inactive'}`} />
          <span>{isRunning ? 'Live Monitoring' : 'Inactive'}</span>
        </div>
      </div>

      <div className="activity-log-body" style={{ maxHeight: '600px', overflowY: 'auto' }}>
        {activities.length === 0 ? (
          <div className="empty-log">
            <Info size={48} />
            <p>No activity yet. Start the bot to see real-time logs.</p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 8px' }}>
            <tbody>
              {activities.map((activity, index) => (
                <tr 
                  key={`${activity.timestamp}-${index}`}
                  style={{
                    backgroundColor: activity.level === 'success' ? 'rgba(16, 185, 129, 0.1)' :
                                   activity.level === 'warning' ? 'rgba(245, 158, 11, 0.1)' :
                                   activity.level === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(59, 130, 246, 0.1)',
                    borderRadius: '8px'
                  }}
                >
                  <td style={{ padding: '12px', width: '40px', borderRadius: '8px 0 0 8px' }}>
                    {getActivityIcon(activity.level)}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <div style={{ fontWeight: 500, marginBottom: '4px' }}>
                      {activity.message}
                    </div>
                    {activity.data && Object.keys(activity.data).length > 0 && (
                      <div style={{ fontSize: '0.85rem', color: '#888', marginTop: '4px' }}>
                        {Object.entries(activity.data).map(([key, value]) => (
                          <span key={key} style={{ marginRight: '12px' }}>
                            <strong>{key}:</strong> {typeof value === 'number' 
                              ? (value % 1 === 0 ? value : value.toFixed(2))
                              : String(value)
                            }
                          </span>
                        ))}
                      </div>
                    )}
                    <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '4px' }}>
                      {formatTime(activity.timestamp)}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <div ref={logEndRef} />
      </div>

      <div className="activity-footer">
        <span className="footer-text">
          Showing {activities.length} recent activities (Server Time)
        </span>
        {isRunning && (
          <span className="live-indicator">
            <span className="pulse-dot" />
            Auto-refreshing every 2s
          </span>
        )}
      </div>
    </div>
  )
}

// Memoize component to prevent re-renders when props haven't actually changed
export default memo(ActivityLog, (prevProps, nextProps) => {
  // Only re-render if activities length changed or isRunning changed
  return prevProps.activities.length === nextProps.activities.length && 
         prevProps.isRunning === nextProps.isRunning
})
