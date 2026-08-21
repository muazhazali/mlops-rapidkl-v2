import type { ForecastResponse } from './types'

export async function fetchForecast(
  startDate: string,
  endDate: string,
  target: string,
): Promise<ForecastResponse> {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
    target,
  })
  const res = await fetch(`/forecast?${params}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Failed to fetch forecast')
  }
  return res.json()
}