import type { WeightEntry } from '../services/weights'

type WeightChartProps = {
  entries: WeightEntry[]
}

function WeightChart({ entries }: WeightChartProps) {
  if (entries.length < 2) {
    return (
      <div className="chart-empty">
        再记录一次体重后，这里会生成趋势折线。
      </div>
    )
  }

  const width = 640
  const height = 280
  const horizontalPadding = 44
  const verticalPadding = 34
  const weights = entries.map((entry) => entry.weight_kg)
  const minimumWeight = Math.min(...weights)
  const maximumWeight = Math.max(...weights)
  const weightRange = Math.max(maximumWeight - minimumWeight, 1)
  const chartWidth = width - horizontalPadding * 2
  const chartHeight = height - verticalPadding * 2
  const timestamps = entries.map((entry) =>
    Date.parse(`${entry.recorded_on}T00:00:00Z`),
  )
  const firstTimestamp = timestamps[0]
  const lastTimestamp = timestamps[timestamps.length - 1]
  const timestampRange = Math.max(
    lastTimestamp - firstTimestamp,
    86_400_000,
  )
  const points = entries.map((entry, index) => {
    const x =
      horizontalPadding +
      ((timestamps[index] - firstTimestamp) / timestampRange) *
        chartWidth
    const y =
      verticalPadding +
      ((maximumWeight - entry.weight_kg) / weightRange) * chartHeight

    return {
      ...entry,
      x,
      y,
    }
  })

  return (
    <div className="weight-chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="体重变化趋势图"
      >
        {[0, 0.5, 1].map((position) => (
          <line
            key={position}
            className="chart-grid-line"
            x1={horizontalPadding}
            x2={width - horizontalPadding}
            y1={verticalPadding + position * chartHeight}
            y2={verticalPadding + position * chartHeight}
          />
        ))}
        <polyline
          className="chart-line"
          points={points.map(({ x, y }) => `${x},${y}`).join(' ')}
        />
        {points.map((point) => (
          <g key={point.id}>
            <circle
              className="chart-point"
              cx={point.x}
              cy={point.y}
              r="6"
            />
            <title>
              {point.recorded_on}: {point.weight_kg} kg
            </title>
            {entries.length <= 10 && (
              <text
                className="chart-value"
                x={point.x}
                y={point.y - 14}
              >
                {point.weight_kg}
              </text>
            )}
          </g>
        ))}
        <text
          className="chart-label"
          x={horizontalPadding}
          y={height - 8}
        >
          {entries[0].recorded_on}
        </text>
        <text
          className="chart-label chart-label--end"
          x={width - horizontalPadding}
          y={height - 8}
        >
          {entries[entries.length - 1].recorded_on}
        </text>
      </svg>
    </div>
  )
}

export default WeightChart
