// components/EpidemicChart.jsx
import { useMemo } from 'react'

export default function EpidemicChart({ history, summary }) {
    // Calculate chart dimensions and scales
    const chartData = useMemo(() => {
        if (!history || !history.S) return null

        const days = history.S.length
        const maxValue = Math.max(
            ...history.S,
            ...history.I,
            ...history.R,
            ...(history.D || [])
        )

        // Use backend summary value for total deaths if available
        const totalDeaths = summary?.total_deaths ?? (history.D?.[history.D.length - 1] || 0)

        return {
            days,
            maxValue,
            susceptible: history.S,
            infected: history.I,
            recovered: history.R,
            deceased: history.D || [],
            totalDeaths
        }
    }, [history, summary])

    if (!chartData) {
        return (
            <div className="bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700">
                <div className="flex flex-col items-center justify-center py-12">
                    <div className="bg-gray-700 rounded-full p-6 mb-4">
                        <span className="text-6xl">📊</span>
                    </div>
                    <p className="text-gray-300 text-lg font-medium">No data available</p>
                    <p className="text-gray-400 text-sm mt-2">Run a simulation to see epidemic curves</p>
                </div>
            </div>
        )
    }

    const { days, maxValue, susceptible, infected, recovered, deceased, totalDeaths } = chartData

    // SVG dimensions
    const width = 800
    const height = 400
    const padding = 60

    // Create path for each series
    const createPath = (data) => {
        const xScale = (width - 2 * padding) / (days - 1)
        const yScale = (height - 2 * padding) / maxValue

        return data
            .map((value, index) => {
                const x = padding + index * xScale
                const y = height - padding - value * yScale
                return `${index === 0 ? 'M' : 'L'} ${x},${y}`
            })
            .join(' ')
    }

    const series = [
        { name: 'Susceptible', data: susceptible, color: '#4CAF50', path: createPath(susceptible) },
        { name: 'Infected', data: infected, color: '#F44336', path: createPath(infected) },
        { name: 'Recovered', data: recovered, color: '#2196F3', path: createPath(recovered) },
        { name: 'Deceased', data: deceased, color: '#757575', path: createPath(deceased) },
    ]

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-6 text-white">📈 Epidemic Curves</h3>

            {/* Legend */}
            <div className="flex flex-wrap gap-4 mb-6">
                {series.map((s, idx) => (
                    <div key={idx} className="flex items-center space-x-2">
                        <div className="w-4 h-4 rounded" style={{ backgroundColor: s.color }}></div>
                        <span className="text-sm text-gray-300 font-medium">{s.name}</span>
                    </div>
                ))}
            </div>

            {/* Chart */}
            <div className="overflow-x-auto">
                <svg
                    width={width}
                    height={height}
                    className="border border-gray-700 rounded-lg bg-gray-800">
                    {/* Grid lines */}
                    {[0, 1, 2, 3, 4].map((i) => {
                        const y = padding + (i * (height - 2 * padding)) / 4
                        return (
                            <g key={i}>
                                <line
                                    x1={padding}
                                    y1={y}
                                    x2={width - padding}
                                    y2={y}
                                    stroke="#e0e0e0"
                                    strokeWidth="1"
                                />
                                <text
                                    x={padding - 10}
                                    y={y + 5}
                                    textAnchor="end"
                                    fontSize="12"
                                    fill="#666"
                                >
                                    {Math.round((maxValue * (4 - i)) / 4)}
                                </text>
                            </g>
                        )
                    })}

                    {/* Vertical grid lines */}
                    {[0, 1, 2, 3, 4].map((i) => {
                        const x = padding + (i * (width - 2 * padding)) / 4
                        return (
                            <g key={`v-${i}`}>
                                <line
                                    x1={x}
                                    y1={padding}
                                    x2={x}
                                    y2={height - padding}
                                    stroke="#e0e0e0"
                                    strokeWidth="1"
                                />
                                <text
                                    x={x}
                                    y={height - padding + 20}
                                    textAnchor="middle"
                                    fontSize="12"
                                    fill="#666"
                                >
                                    {Math.round((days * i) / 4)}
                                </text>
                            </g>
                        )
                    })}

                    {/* Axes */}
                    <line
                        x1={padding}
                        y1={height - padding}
                        x2={width - padding}
                        y2={height - padding}
                        stroke="#333"
                        strokeWidth="2"
                    />
                    <line
                        x1={padding}
                        y1={padding}
                        x2={padding}
                        y2={height - padding}
                        stroke="#333"
                        strokeWidth="2"
                    />

                    {/* Data lines */}
                    {series.map((s, idx) => (
                        <path
                            key={idx}
                            d={s.path}
                            fill="none"
                            stroke={s.color}
                            strokeWidth="3"
                            strokeLinejoin="round"
                            strokeLinecap="round"
                        />
                    ))}

                    {/* Axis labels */}
                    <text
                        x={width / 2}
                        y={height - 10}
                        textAnchor="middle"
                        fontSize="14"
                        fill="#333"
                        fontWeight="bold"
                    >
                        Days
                    </text>
                    <text
                        x={15}
                        y={height / 2}
                        textAnchor="middle"
                        fontSize="14"
                        fill="#333"
                        fontWeight="bold"
                        transform={`rotate(-90, 15, ${height / 2})`}
                    >
                        Population
                    </text>
                </svg>
            </div>

            {/* Summary Statistics */}
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="bg-gray-700 rounded-lg p-3 border border-gray-600">
                    <div className="text-xs text-gray-300 uppercase">Final Susceptible</div>
                    <div className="text-xl font-bold text-green-400">{susceptible[susceptible.length - 1]}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-3 border border-gray-600">
                    <div className="text-xs text-gray-300 uppercase">Peak Infected</div>
                    <div className="text-xl font-bold text-red-400">{Math.max(...infected)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-3 border border-gray-600">
                    <div className="text-xs text-gray-300 uppercase">Total Recovered</div>
                    <div className="text-xl font-bold text-blue-400">{recovered[recovered.length - 1]}</div>
                </div>
                <div className={`bg-gray-700 rounded-lg p-3 border-2 ${totalDeaths > 0 ? 'border-red-600' : 'border-green-600'}`}>
                    <div className="text-xs text-gray-300 uppercase">Total Deaths</div>
                    <div className={`text-xl font-bold ${totalDeaths > 0 ? 'text-red-400' : 'text-green-400'}`}>
                        {totalDeaths}
                    </div>
                    {totalDeaths === 0 && (
                        <div className="text-xs text-green-400 mt-1">✓ Zero fatalities</div>
                    )}
                </div>
            </div>
        </div>
    )
}
