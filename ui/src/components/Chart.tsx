import { useEffect, useRef } from 'react'
import { createChart, IChartApi } from 'lightweight-charts'

interface OHLCVData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface ChartProps {
  data: OHLCVData[] | any[]
  symbol: string
}

export default function Chart({ data, symbol }: ChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<any>(null)
  const volumeSeriesRef = useRef<any>(null)

  useEffect(() => {
    if (!chartContainerRef.current || !data || data.length === 0) {
      console.log('Chart: No data or container', { hasContainer: !!chartContainerRef.current, dataLength: data?.length })
      return
    }

    console.log('Chart: Rendering with data', { dataLength: data.length, firstItem: data[0] })

    // Clean up existing chart
    if (chartRef.current) {
      chartRef.current.remove()
      chartRef.current = null
    }

    // Create new chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 500,
      layout: {
        background: { color: 'transparent' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: 'rgba(209, 212, 220, 0.1)' },
        horzLines: { color: 'rgba(209, 212, 220, 0.1)' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: 'rgba(209, 212, 220, 0.2)',
      },
      rightPriceScale: {
        borderColor: 'rgba(209, 212, 220, 0.2)',
      },
    })

    chartRef.current = chart

    // Add candlestick series using correct API
    const candlestickSeries = (chart as any).addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    candlestickSeriesRef.current = candlestickSeries

    // Add volume series using correct API
    const volumeSeries = (chart as any).addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    })

    volumeSeriesRef.current = volumeSeries

    // Configure volume scale
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    })

    // Format and set data
    try {
      // Check if data is array format [timestamp, open, high, low, close, volume]
      const isArrayFormat = Array.isArray(data[0])
      
      console.log('Chart: Data format check', { isArrayFormat, firstItem: data[0] })

      let normalizedData: OHLCVData[]
      
      if (isArrayFormat) {
        // Convert array format to object format
        normalizedData = data.map((item: any) => ({
          timestamp: item[0],
          open: item[1],
          high: item[2],
          low: item[3],
          close: item[4],
          volume: item[5] || 0
        }))
        console.log('Chart: Converted array to OHLCV', { first: normalizedData[0] })
      } else {
        // Already in object format
        const hasOHLCV = data[0] && 
          typeof data[0].open !== 'undefined' && 
          typeof data[0].high !== 'undefined' && 
          typeof data[0].low !== 'undefined' && 
          typeof data[0].close !== 'undefined'

        if (!hasOHLCV) {
          console.error('Chart: Invalid OHLCV data format. Expected: {timestamp, open, high, low, close, volume} or [timestamp, open, high, low, close, volume]')
          console.error('Chart: Received data:', data[0])
          return
        }
        normalizedData = data
      }

      const formattedCandleData = normalizedData.map(item => {
        // Convert timestamp to seconds if it's in milliseconds
        let timestamp = item.timestamp
        if (timestamp > 10000000000) {
          timestamp = Math.floor(timestamp / 1000)
        }

        return {
          time: timestamp as any,
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }
      })

      const formattedVolumeData = normalizedData.map(item => {
        // Convert timestamp to seconds if it's in milliseconds
        let timestamp = item.timestamp
        if (timestamp > 10000000000) {
          timestamp = Math.floor(timestamp / 1000)
        }

        return {
          time: timestamp as any,
          value: item.volume || 0,
          color: item.close >= item.open ? '#26a69a80' : '#ef535080',
        }
      })

      console.log('Chart: Setting data', { 
        candleDataLength: formattedCandleData.length, 
        volumeDataLength: formattedVolumeData.length,
        firstCandle: formattedCandleData[0],
        firstVolume: formattedVolumeData[0]
      })

      candlestickSeries.setData(formattedCandleData)
      volumeSeries.setData(formattedVolumeData)

      // Fit content to view
      chart.timeScale().fitContent()
      
      console.log('Chart: Rendering complete')
    } catch (error) {
      console.error('Error formatting chart data:', error)
    }

    // Handle window resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
      }
    }
  }, [data])

  // Calculate time range
  const getTimeRange = () => {
    if (!data || data.length === 0) return 'No data'
    
    // Handle both array and object format
    const firstTimestamp = Array.isArray(data[0]) ? data[0][0] : data[0].timestamp
    const lastTimestamp = Array.isArray(data[data.length - 1]) ? data[data.length - 1][0] : data[data.length - 1].timestamp
    
    // Convert to milliseconds if needed
    const first = firstTimestamp > 10000000000 ? firstTimestamp : firstTimestamp * 1000
    const last = lastTimestamp > 10000000000 ? lastTimestamp : lastTimestamp * 1000
    
    const diffMs = last - first
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffDays > 0) {
      return `Last ${diffDays} Day${diffDays > 1 ? 's' : ''}`
    } else if (diffHours > 0) {
      return `Last ${diffHours} Hour${diffHours > 1 ? 's' : ''}`
    } else {
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return `Last ${diffMinutes} Minute${diffMinutes > 1 ? 's' : ''}`
    }
  }

  return (
    <div className="card chart-card">
      <div className="card-header">
        <h3>{symbol} - {getTimeRange()}</h3>
        <span className="text-secondary">{data.length} candles</span>
      </div>
      <div ref={chartContainerRef} className="chart-container" style={{ minHeight: '500px' }} />
    </div>
  )
}