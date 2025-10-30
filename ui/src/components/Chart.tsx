import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

interface ChartProps {
  data: number[][]
  symbol: string
}

export default function Chart({ data, symbol }: ChartProps) {
  // Transform OHLCV data to chart format
  const chartData = data.map((candle) => ({
    time: new Date(candle).toLocaleTimeString(),
    price: candle, // Close price
    volume: candle
  }))

  return (
    <div className="card">
      <h3>{symbol} - Last 24 Hours</h3>
      <div style={{ width: '100%', height: 400 }}>
        <ResponsiveContainer>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px'
              }}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
