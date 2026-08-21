export interface ForecastPoint {
  date: string
  actual: number | null
  predicted: number | null
}

export interface ForecastResponse {
  target: string
  start_date: string
  end_date: string
  points: ForecastPoint[]
}