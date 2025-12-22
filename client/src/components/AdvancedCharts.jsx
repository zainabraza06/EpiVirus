// components/AdvancedCharts.jsx - Comprehensive visualization components

// Disease Dynamics Stacked Area Chart
export function DiseaseDynamicsChart({ history }) {
    if (!history || !history.S) return null

    const days = history.S.length
    const width = 800
    const height = 400
    const padding = 60

    // Find max value for scaling
    const maxValue = Math.max(
        ...history.S,
        ...history.I,
        ...history.R,
        ...(history.D || [])
    )

    const xScale = (width - 2 * padding) / (days - 1)
    const yScale = (height - 2 * padding) / maxValue

    // Create stacked area paths
    const createAreaPath = (data, baseData = null) => {
        return data
            .map((value, index) => {
                const x = padding + index * xScale
                const baseY = baseData
                    ? height - padding - (baseData[index] || 0) * yScale
                    : height - padding
                const y = baseY - value * yScale
                return `${index === 0 ? 'M' : 'L'} ${x},${y}`
            })
            .join(' ') +
            ` L ${padding + (days - 1) * xScale},${height - padding} ` +
            `L ${padding},${height - padding} Z`
    }

    // Stack the areas: S, then S+I, then S+I+R, then S+I+R+D
    const deathsStacked = history.S.map((s, i) => s + history.I[i] + history.R[i] + (history.D?.[i] || 0))
    const recoveredStacked = history.S.map((s, i) => s + history.I[i] + history.R[i])
    const infectedStacked = history.S.map((s, i) => s + history.I[i])

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Disease Dynamics Over Time</h3>

            <svg width={width} height={height} className="border border-gray-700 rounded-lg">
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

                {/* Stacked area paths - ordered from top (deaths) to bottom (susceptible) */}
                <path
                    d={createAreaPath(deathsStacked)}
                    fill="#757575"
                    opacity="0.7"
                />
                <path
                    d={createAreaPath(recoveredStacked)}
                    fill="#2196F3"
                    opacity="0.7"
                />
                <path
                    d={createAreaPath(infectedStacked)}
                    fill="#F44336"
                    opacity="0.7"
                />
                <path
                    d={createAreaPath(history.S)}
                    fill="#4CAF50"
                    opacity="0.7"
                />

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

                {/* Labels */}
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
                    Individuals
                </text>
            </svg>

            {/* Legend */}
            <div className="flex justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-green-500 rounded opacity-70"></div>
                    <span className="text-sm font-medium">Susceptible</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-red-500 rounded opacity-70"></div>
                    <span className="text-sm font-medium">Infectious</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-blue-500 rounded opacity-70"></div>
                    <span className="text-sm font-medium">Recovered</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-gray-500 rounded opacity-70"></div>
                    <span className="text-sm font-medium">Deceased</span>
                </div>
            </div>
        </div>
    )
}

// Daily New Cases with 7-day Average
export function DailyNewCasesChart({ dailyCases }) {
    if (!dailyCases || dailyCases.length === 0) return null

    const width = 800
    const height = 400
    const padding = 60

    const maxCases = Math.max(...dailyCases, 1)
    const xScale = (width - 2 * padding) / dailyCases.length
    const yScale = (height - 2 * padding) / maxCases

    // Calculate 7-day moving average
    const movingAverage = dailyCases.map((_, i) => {
        const start = Math.max(0, i - 6)
        const window = dailyCases.slice(start, i + 1)
        return window.reduce((a, b) => a + b, 0) / window.length
    })

    // Find peak day
    const peakDay = dailyCases.indexOf(Math.max(...dailyCases))

    // Create 7-day average line path
    const avgPath = movingAverage
        .map((value, i) => {
            const x = padding + i * xScale
            const y = height - padding - value * yScale
            return `${i === 0 ? 'M' : 'L'} ${x},${y}`
        })
        .join(' ')

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Epidemic Curve - Daily New Cases</h3>

            <svg width={width} height={height} className="border border-gray-700 rounded-lg bg-gray-800">
                {/* Grid */}
                {[0, 1, 2, 3, 4].map((i) => {
                    const y = padding + (i * (height - 2 * padding)) / 4
                    return (
                        <line
                            key={i}
                            x1={padding}
                            y1={y}
                            x2={width - padding}
                            y2={y}
                            stroke="#e0e0e0"
                            strokeWidth="1"
                        />
                    )
                })}

                {/* Daily bars */}
                {dailyCases.map((cases, i) => {
                    const x = padding + i * xScale
                    const barHeight = cases * yScale
                    const y = height - padding - barHeight
                    return (
                        <rect
                            key={i}
                            x={x}
                            y={y}
                            width={Math.max(xScale - 1, 1)}
                            height={barHeight}
                            fill="#F44336"
                            opacity="0.6"
                        />
                    )
                })}

                {/* 7-day moving average line */}
                <path
                    d={avgPath}
                    fill="none"
                    stroke="#8B0000"
                    strokeWidth="3"
                    strokeLinejoin="round"
                />

                {/* Peak day marker */}
                <line
                    x1={padding + peakDay * xScale}
                    y1={padding}
                    x2={padding + peakDay * xScale}
                    y2={height - padding}
                    stroke="#FF6B6B"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                />
                <text
                    x={padding + peakDay * xScale + 5}
                    y={padding + 20}
                    fontSize="12"
                    fill="#FF6B6B"
                    fontWeight="bold"
                >
                    Peak (Day {peakDay})
                </text>

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

                <text x={width / 2} y={height - 10} textAnchor="middle" fontSize="14" fill="#333" fontWeight="bold">
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
                    New Infections
                </text>
            </svg>

            {/* Legend */}
            <div className="flex justify-center gap-6 mt-4">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-red-500 rounded opacity-60"></div>
                    <span className="text-sm font-medium">Daily Cases</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-8 h-0.5 bg-red-900"></div>
                    <span className="text-sm font-medium">7-day Average</span>
                </div>
            </div>
        </div>
    )
}

// Healthcare System Burden Chart
export function HealthcareSystemChart({ severityData, capacity }) {
    if (!severityData || !severityData.hospitalized) return null

    const width = 800
    const height = 400
    const padding = 60

    const days = severityData.hospitalized.length
    const maxValue = Math.max(
        ...severityData.asymptomatic.map((a, i) =>
            a + severityData.mild[i] + severityData.severe[i] +
            severityData.hospitalized[i] + severityData.critical[i]
        ),
        capacity
    )

    const xScale = (width - 2 * padding) / (days - 1)
    const yScale = (height - 2 * padding) / maxValue

    const createStackedPath = (data, previousStacks) => {
        const points = data.map((value, i) => {
            const x = padding + i * xScale
            const baseY = previousStacks ?
                height - padding - previousStacks[i] * yScale :
                height - padding
            const y = baseY - value * yScale
            return `${i === 0 ? 'M' : 'L'} ${x},${y}`
        })

        const closePath = [...previousStacks].reverse().map((value, i) => {
            const x = padding + (days - 1 - i) * xScale
            const y = height - padding - value * yScale
            return `L ${x},${y}`
        })

        return points.join(' ') + ' ' + closePath.join(' ') + ' Z'
    }

    // Calculate cumulative stacks
    const stack1 = severityData.asymptomatic
    const stack2 = severityData.asymptomatic.map((a, i) => a + severityData.mild[i])
    const stack3 = stack2.map((s, i) => s + severityData.severe[i])
    const stack4 = stack3.map((s, i) => s + severityData.hospitalized[i])

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Healthcare System Burden</h3>

            <svg width={width} height={height} className="border border-gray-700 rounded-lg bg-gray-800">
                {/* Grid */}
                {[0, 1, 2, 3, 4].map((i) => {
                    const y = padding + (i * (height - 2 * padding)) / 4
                    return (
                        <line
                            key={i}
                            x1={padding}
                            y1={y}
                            x2={width - padding}
                            y2={y}
                            stroke="#e0e0e0"
                            strokeWidth="1"
                        />
                    )
                })}

                {/* Stacked areas */}
                <path d={createStackedPath(severityData.critical, stack4)} fill="#8B0000" opacity="0.8" />
                <path d={createStackedPath(severityData.hospitalized, stack3)} fill="#DC143C" opacity="0.7" />
                <path d={createStackedPath(severityData.severe, stack2)} fill="#FF6B6B" opacity="0.6" />
                <path d={createStackedPath(severityData.mild, stack1)} fill="#FFB6C1" opacity="0.5" />
                <path d={createStackedPath(severityData.asymptomatic, new Array(days).fill(0))} fill="#FFE4E1" opacity="0.4" />

                {/* ICU Capacity line */}
                <line
                    x1={padding}
                    y1={height - padding - capacity * yScale}
                    x2={width - padding}
                    y2={height - padding - capacity * yScale}
                    stroke="#FF0000"
                    strokeWidth="2"
                    strokeDasharray="10,5"
                />
                <text
                    x={width - padding - 120}
                    y={height - padding - capacity * yScale - 5}
                    fontSize="12"
                    fill="#FF0000"
                    fontWeight="bold"
                >
                    ICU Capacity ({Math.round(capacity)})
                </text>

                {/* Axes */}
                <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#333" strokeWidth="2" />
                <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#333" strokeWidth="2" />

                <text x={width / 2} y={height - 10} textAnchor="middle" fontSize="14" fill="#333" fontWeight="bold">Days</text>
                <text x={15} y={height / 2} textAnchor="middle" fontSize="14" fill="#333" fontWeight="bold" transform={`rotate(-90, 15, ${height / 2})`}>
                    Patients
                </text>
            </svg>

            {/* Legend */}
            <div className="grid grid-cols-5 gap-4 mt-4">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FFE4E1', opacity: 0.4 }}></div>
                    <span className="text-xs">Asymptomatic</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FFB6C1', opacity: 0.5 }}></div>
                    <span className="text-xs">Mild</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FF6B6B', opacity: 0.6 }}></div>
                    <span className="text-xs">Severe</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: '#DC143C', opacity: 0.7 }}></div>
                    <span className="text-xs">Hospitalized</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: '#8B0000', opacity: 0.8 }}></div>
                    <span className="text-xs">Critical</span>
                </div>
            </div>
        </div>
    )
}

// Age Distribution Histogram
export function AgeDistributionChart({ ageData }) {
    if (!ageData || !ageData.bins || !ageData.counts) return null

    const width = 400
    const height = 300
    const padding = 50

    const maxCount = Math.max(...ageData.counts, 1)
    const barWidth = (width - 2 * padding) / ageData.counts.length
    const yScale = (height - 2 * padding) / maxCount

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-white">Age Distribution of Infections</h3>

            <svg width={width} height={height} className="border border-gray-200 rounded-lg bg-gray-50">
                {/* Bars */}
                {ageData.counts.map((count, i) => (
                    <rect
                        key={i}
                        x={padding + i * barWidth}
                        y={height - padding - count * yScale}
                        width={barWidth - 2}
                        height={count * yScale}
                        fill="#F44336"
                        opacity="0.7"
                    />
                ))}

                {/* Axes */}
                <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#333" strokeWidth="2" />
                <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#333" strokeWidth="2" />

                {/* Labels */}
                {ageData.bins.slice(0, -1).map((bin, i) => (
                    <text
                        key={i}
                        x={padding + i * barWidth + barWidth / 2}
                        y={height - padding + 20}
                        textAnchor="middle"
                        fontSize="10"
                        fill="#666"
                    >
                        {bin}
                    </text>
                ))}

                <text x={width / 2} y={height - 5} textAnchor="middle" fontSize="12" fill="#333" fontWeight="bold">Age</text>
                <text x={10} y={height / 2} textAnchor="middle" fontSize="12" fill="#333" fontWeight="bold" transform={`rotate(-90, 10, ${height / 2})`}>
                    Count
                </text>
            </svg>
        </div>
    )
}

// Degree Distribution Histogram
export function DegreeDistributionChart({ degreeData }) {
    if (!degreeData || !degreeData.bins || !degreeData.counts) return null

    const width = 400
    const height = 300
    const padding = 50

    const maxCount = Math.max(...degreeData.counts, 1)
    const barWidth = (width - 2 * padding) / degreeData.counts.length
    const yScale = (height - 2 * padding) / maxCount

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-white">Degree Distribution</h3>

            <svg width={width} height={height} className="border border-gray-200 rounded-lg bg-gray-50">
                {/* Bars */}
                {degreeData.counts.map((count, i) => (
                    <rect
                        key={i}
                        x={padding + i * barWidth}
                        y={height - padding - count * yScale}
                        width={Math.max(barWidth - 2, 1)}
                        height={count * yScale}
                        fill="#2196F3"
                        opacity="0.7"
                    />
                ))}

                {/* Axes */}
                <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#333" strokeWidth="2" />
                <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#333" strokeWidth="2" />

                <text x={width / 2} y={height - 5} textAnchor="middle" fontSize="12" fill="#333" fontWeight="bold">Degree</text>
                <text x={10} y={height / 2} textAnchor="middle" fontSize="12" fill="#333" fontWeight="bold" transform={`rotate(-90, 10, ${height / 2})`}>
                    Frequency
                </text>
            </svg>
        </div>
    )
}
