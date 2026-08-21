import type { ForecastPoint } from '../types'

interface Props {
  point: ForecastPoint | null
}

export function CurrentValueCard({ point }: Props) {
  if (!point) {
    return <div className="value-card empty">No data yet</div>
  }

  const actual = point.actual !== null ? Math.round(point.actual).toLocaleString() : '—'
  const predicted =
    point.predicted !== null ? Math.round(point.predicted).toLocaleString() : '—'

  let error: string | null = null
  if (point.actual !== null && point.predicted !== null) {
    const diff = Math.abs(point.actual - point.predicted)
    const pct = (diff / point.actual) * 100
    error = `${Math.round(diff).toLocaleString()} (${pct.toFixed(1)}%)`
  }

  return (
    <div className="value-card">
      <div className="value-card-date">{point.date}</div>
      <div className="value-card-grid">
        <div className="value-item">
          <span className="value-label">Actual</span>
          <span className="value-number actual">{actual}</span>
        </div>
        <div className="value-item">
          <span className="value-label">Predicted</span>
          <span className="value-number predicted">{predicted}</span>
        </div>
        <div className="value-item">
          <span className="value-label">Error</span>
          <span className="value-number error">{error ?? '—'}</span>
        </div>
      </div>
    </div>
  )
}