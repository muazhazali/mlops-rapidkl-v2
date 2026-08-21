import { useState } from 'react'
import './App.css'
import { fetchForecast } from './api'
import type { ForecastPoint } from './types'
import { ForecastChart } from './components/ForecastChart'

function App() {
  const today = new Date()
  const defaultEnd = new Date(today)
  defaultEnd.setMonth(defaultEnd.getMonth() + 6)

  const [startDate, setStartDate] = useState('2026-01-01')
  const [endDate, setEndDate] = useState(defaultEnd.toISOString().slice(0, 10))
  const [target, setTarget] = useState('rail_mrt_kajang')
  const [data, setData] = useState<ForecastPoint[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFetch = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetchForecast(startDate, endDate, target)
      setData(res.points)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const actualCount = data.filter((p) => p.actual !== null).length
  const predictedCount = data.filter((p) => p.predicted !== null).length

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

      {data.length > 0 && (
        <>
          <div className="stats">
            <span>Actual: {actualCount} days</span>
            <span>Predicted: {predictedCount} days</span>
          </div>
          <div className="chart-container">
            <ForecastChart data={data} />
          </div>
        </>
      )}

      {data.length === 0 && !loading && !error && (
        <div className="placeholder">
          Select a date range and click "Fetch Forecast" to see the chart.
        </div>
      )}
    </div>
  )
}

export default App