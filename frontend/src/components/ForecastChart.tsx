import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from 'recharts'
import type { ForecastPoint } from '../types'

interface Props {
  data: ForecastPoint[]
}

export function ForecastChart({ data }: Props) {
  const chartData = data.map((p) => ({
    date: p.date,
    actual: p.actual,
    predicted: p.predicted,
  }))

  return (
    <ResponsiveContainer width="100%" height={450}>
      <LineChart data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          interval="preserveStartEnd"
          minTickGap={30}
        />
        <YAxis
          tick={{ fontSize: 12 }}
          tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}K`}
        />
        <Tooltip
          formatter={(value) => Number(value).toLocaleString()}
          labelStyle={{ fontWeight: 600 }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="actual"
          stroke="#2563eb"
          strokeWidth={2}
          dot={false}
          name="Actual"
          connectNulls={false}
        />
        <Line
          type="monotone"
          dataKey="predicted"
          stroke="#ea580c"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
          name="Predicted"
          connectNulls={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}