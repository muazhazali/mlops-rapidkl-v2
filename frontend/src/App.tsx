import { useState, useEffect, useRef, useCallback } from 'react'
import './App.css'
import { fetchForecast } from './api'
import type { ForecastPoint } from './types'
import { ForecastChart } from './components/ForecastChart'
import { CurrentValueCard } from './components/CurrentValueCard'

const SPEED_OPTIONS = [0.5, 1, 2, 4] as const
const BASE_INTERVAL_MS = 1000

function App() {
  const today = new Date()
  const defaultEnd = new Date(today)
  defaultEnd.setMonth(defaultEnd.getMonth() + 6)

  const [startDate, setStartDate] = useState('2026-01-01')
  const [endDate, setEndDate] = useState(defaultEnd.toISOString().slice(0, 10))
  const [target, setTarget] = useState('rail_mrt_kajang')
  const [fullData, setFullData] = useState<ForecastPoint[]>([])
  const [visibleCount, setVisibleCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const handleFetch = async () => {
    setLoading(true)
    setError(null)
    setIsPlaying(false)
    setVisibleCount(0)
    try {
      const res = await fetchForecast(startDate, endDate, target)
      setFullData(res.points)
      setVisibleCount(1)
      setIsPlaying(true)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const stopPlayback = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setIsPlaying(false)
  }, [])

  const startPlayback = useCallback(() => {
    if (fullData.length === 0) return
    if (visibleCount >= fullData.length) {
      setVisibleCount(1)
    }
    setIsPlaying(true)
  }, [fullData.length, visibleCount])

  useEffect(() => {
    if (!isPlaying || fullData.length === 0) return

    const intervalMs = BASE_INTERVAL_MS / speed
    intervalRef.current = setInterval(() => {
      setVisibleCount((prev) => {
        if (prev >= fullData.length) {
          if (intervalRef.current !== null) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
          setIsPlaying(false)
          return prev
        }
        return prev + 1
      })
    }, intervalMs)

    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isPlaying, fullData.length, speed])

  useEffect(() => {
    return () => stopPlayback()
  }, [stopPlayback])

  const handleReset = () => {
    stopPlayback()
    setVisibleCount(1)
  }

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    stopPlayback()
    setVisibleCount(Number(e.target.value))
  }

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed)
  }

  const visibleData = fullData.slice(0, visibleCount)
  const actualCount = visibleData.filter((p) => p.actual !== null).length
  const predictedCount = visibleData.filter((p) => p.predicted !== null).length
  const currentPoint = visibleData.length > 0 ? visibleData[visibleData.length - 1] : null
  const isComplete = visibleCount >= fullData.length && fullData.length > 0
  const progressPct =
    fullData.length > 0 ? (visibleCount / fullData.length) * 100 : 0

  return (
    <div className="app">
      <header className="header">
        <h1>RapidKL Ridership Forecast</h1>
        <p className="subtitle">
          Actual vs predicted daily ridership from {startDate} to {endDate}
        </p>
      </header>

      <section className="controls">
        <label>
          Start
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </label>
        <label>
          End
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </label>
        <label>
          Target
          <select value={target} onChange={(e) => setTarget(e.target.value)}>
            <option value="rail_mrt_kajang">MRT Kajang</option>
            <option value="rail_mrt_pjy">MRT PJY</option>
            <option value="rail_lrt_kj">LRT Kelana Jaya</option>
            <option value="rail_lrt_ampang">LRT Ampang</option>
            <option value="rail_monorail">Monorail</option>
          </select>
        </label>
        <button onClick={handleFetch} disabled={loading}>
          {loading ? 'Loading...' : 'Fetch Forecast'}
        </button>
      </section>

      {error && <div className="error">{error}</div>}

      {fullData.length > 0 && (
        <>
          <div className="value-card-row">
            <CurrentValueCard point={currentPoint} />
          </div>

          <div className="playback-controls">
            {!isPlaying ? (
              <button
                className="play-btn"
                onClick={startPlayback}
                disabled={isComplete}
              >
                ▶ Play
              </button>
            ) : (
              <button className="play-btn" onClick={stopPlayback}>
                ⏸ Pause
              </button>
            )}
            <button className="reset-btn" onClick={handleReset}>
              ↺ Reset
            </button>
            <div className="speed-control">
              <span className="speed-label">Speed</span>
              {SPEED_OPTIONS.map((s) => (
                <button
                  key={s}
                  className={`speed-btn ${speed === s ? 'active' : ''}`}
                  onClick={() => handleSpeedChange(s)}
                >
                  {s}x
                </button>
              ))}
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progressPct}%` }} />
            </div>
            <span className="progress-text">
              {visibleCount} / {fullData.length}
            </span>
          </div>

          <input
            type="range"
            min={1}
            max={fullData.length}
            value={visibleCount}
            onChange={handleSliderChange}
            className="scrubber"
          />

          <div className="stats">
            <span>Actual: {actualCount} days</span>
            <span>Predicted: {predictedCount} days</span>
          </div>

          <div className="chart-container">
            <ForecastChart
              data={visibleData}
              fullDateRange={
                fullData.length > 0
                  ? {
                      start: fullData[0].date,
                      end: fullData[fullData.length - 1].date,
                    }
                  : null
              }
            />
          </div>
        </>
      )}

      {fullData.length === 0 && !loading && !error && (
        <div className="placeholder">
          Select a date range and click "Fetch Forecast" to see the chart.
        </div>
      )}
    </div>
  )
}

export default App