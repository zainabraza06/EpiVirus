// components/ComprehensiveCharts.jsx - Complete visualization suite using Recharts
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    RadarChart,
    Radar,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    ScatterChart,
    Scatter,
    RadialBarChart,
    RadialBar,
    Treemap,
    XAxis,
    YAxis,
    ZAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ComposedChart
} from 'recharts'

const COLORS = {
    susceptible: '#4CAF50',
    exposed: '#FF9800',
    infected: '#F44336',
    recovered: '#2196F3',
    deceased: '#757575',
    vaccinated: '#9C27B0'
}

// NEW: Disease Dynamics Over Time (matching backend image style)
export function DiseaseDynamicsStacked({ history }) {
    if (!history || !history.S) return null

    const data = history.S.map((s, i) => ({
        day: i,
        Susceptible: s,
        Infectious: history.I[i],
        Recovered: history.R[i],
        Deceased: history.D?.[i] || 0
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Disease Dynamics Over Time</h3>
            <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="day"
                        label={{ value: 'Days', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        label={{ value: 'Individuals', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Legend
                        verticalAlign="top"
                        height={36}
                        wrapperStyle={{ paddingBottom: '10px' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="Susceptible"
                        stackId="1"
                        stroke="#4CAF50"
                        fill="#4CAF50"
                        fillOpacity={0.6}
                    />
                    <Area
                        type="monotone"
                        dataKey="Infectious"
                        stackId="1"
                        stroke="#FF6B6B"
                        fill="#FF6B6B"
                        fillOpacity={0.6}
                    />
                    <Area
                        type="monotone"
                        dataKey="Recovered"
                        stackId="1"
                        stroke="#2196F3"
                        fill="#2196F3"
                        fillOpacity={0.6}
                    />
                    <Area
                        type="monotone"
                        dataKey="Deceased"
                        stackId="1"
                        stroke="#757575"
                        fill="#757575"
                        fillOpacity={0.6}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Epidemic Curve (matching backend image style)
export function EpidemicCurveChart({ history }) {
    if (!history || !history.I) return null

    // Calculate daily new infections
    const dailyNew = history.I.map((current, i) => {
        const prev = i > 0 ? history.I[i - 1] : 0
        return Math.max(0, current - prev)
    })

    // Calculate 7-day moving average
    const calculateMovingAvg = (data, window = 7) => {
        return data.map((_, i) => {
            const start = Math.max(0, i - window + 1)
            const slice = data.slice(start, i + 1)
            return slice.reduce((a, b) => a + b, 0) / slice.length
        })
    }

    const movingAvg = calculateMovingAvg(dailyNew)
    const peakDay = dailyNew.indexOf(Math.max(...dailyNew))

    const data = dailyNew.map((cases, i) => ({
        day: i,
        'Daily Cases': cases,
        '7 day avg': movingAvg[i],
        isPeak: i === peakDay
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Epidemic Curve</h3>
            <ResponsiveContainer width="100%" height={350}>
                <ComposedChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="day"
                        label={{ value: 'Days', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        label={{ value: 'New Infections', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Legend
                        verticalAlign="top"
                        height={36}
                        payload={[
                            { value: '7 day avg', type: 'line', color: '#8B0000' },
                            { value: `Peak (Day ${peakDay})`, type: 'line', color: '#FF1744', strokeDasharray: '5 5' },
                            { value: 'Daily Cases', type: 'rect', color: '#FF6B6B' }
                        ]}
                    />
                    <Bar dataKey="Daily Cases" fill="#FF6B6B" opacity={0.8} />
                    <Line
                        type="monotone"
                        dataKey="7 day avg"
                        stroke="#8B0000"
                        strokeWidth={2.5}
                        dot={false}
                    />
                    {/* Peak day vertical line */}
                    <Line
                        type="monotone"
                        dataKey={peakDay}
                        stroke="#FF1744"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={false}
                    />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Healthcare System Burden (matching backend image style)
export function HealthcareSystemChart({ severityData, capacity = 50 }) {
    if (!severityData || !severityData.hospitalized) return null

    const data = severityData.hospitalized.map((_, i) => ({
        day: i,
        Asymptomatic: severityData.asymptomatic[i],
        Mild: severityData.mild[i],
        Severe: severityData.severe[i],
        Hospitalized: severityData.hospitalized[i],
        ICUCapacity: capacity
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Healthcare System Burden</h3>
            <ResponsiveContainer width="100%" height={350}>
                <ComposedChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="day"
                        label={{ value: 'Days', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        label={{ value: 'Patients', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Legend
                        verticalAlign="top"
                        height={36}
                        wrapperStyle={{ paddingBottom: '10px' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="Asymptomatic"
                        stackId="1"
                        stroke="#FFFACD"
                        fill="#FFFACD"
                        fillOpacity={0.7}
                    />
                    <Area
                        type="monotone"
                        dataKey="Mild"
                        stackId="1"
                        stroke="#FFE4B5"
                        fill="#FFE4B5"
                        fillOpacity={0.7}
                    />
                    <Area
                        type="monotone"
                        dataKey="Severe"
                        stackId="1"
                        stroke="#FFB6C1"
                        fill="#FFB6C1"
                        fillOpacity={0.7}
                    />
                    <Area
                        type="monotone"
                        dataKey="Hospitalized"
                        stackId="1"
                        stroke="#FF69B4"
                        fill="#FF69B4"
                        fillOpacity={0.7}
                    />
                    <Line
                        type="monotone"
                        dataKey="ICUCapacity"
                        stroke="#DC143C"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={false}
                        name={`ICU Capacity (${capacity})`}
                    />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Simulation Summary Box (matching backend image style)
export function SimulationSummary({ simulationResults }) {
    if (!simulationResults) return null

    const { history, detailed_data } = simulationResults
    const lastDay = history.S.length - 1
    const peakInfections = Math.max(...history.I)
    const peakDay = history.I.indexOf(peakInfections)
    const totalRecovered = history.R[lastDay]
    const totalDeaths = history.D?.[lastDay] || 0
    const totalPopulation = history.S[0] + history.I[0] + history.R[0]
    const attackRate = ((totalRecovered + totalDeaths) / totalPopulation * 100).toFixed(1)
    const caseFatalityRate = totalDeaths > 0 && (totalRecovered + totalDeaths) > 0
        ? (totalDeaths / (totalRecovered + totalDeaths) * 100).toFixed(2)
        : 0.00

    const totalVaccinated = detailed_data?.vaccination_data?.total_vaccinated || 0
    const totalHospitalized = detailed_data?.severity_breakdown?.hospitalized?.[lastDay] || 0
    const finalSusceptible = history.S[lastDay]

    return (
        <div className="bg-blue-900 text-white rounded-lg shadow-xl p-6">
            <h3 className="text-xl font-bold mb-4 text-center bg-blue-800 py-2 px-4 rounded">
                SIMULATION SUMMARY
            </h3>
            <div className="space-y-1 text-sm font-mono">
                <p>□ {totalPopulation} Population | {lastDay} Days</p>
                <p>□ Attack Rate: {attackRate}%</p>
                <p>□ Peak Infections: {peakInfections} (Day {peakDay})</p>
                <p>□ Total Deaths: {totalDeaths}</p>
                <p>□ Case Fatality Rate: {caseFatalityRate}%</p>
                <p>□ Total Vaccinated: {totalVaccinated}</p>
                <p>□ Total Hospitalized: {totalHospitalized}</p>
                <p>□ Total Hospitalized: {totalHospitalized}</p>
                <p>□ Final Susceptible: {finalSusceptible}</p>
                <p>□ Total Recovered: {totalRecovered}</p>
            </div>
        </div>
    )
}

// NEW: SEIRD Dynamics (5 lines - matching backend image)
export function SEIRDDynamicsChart({ history }) {
    if (!history || !history.S) return null

    const data = history.S.map((s, i) => ({
        day: i,
        Susceptible: s,
        Exposed: history.E?.[i] || 0,
        Infected: history.I[i],
        Recovered: history.R[i],
        Deceased: history.D?.[i] || 0
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">SEIRD Dynamics</h3>
            <ResponsiveContainer width="100%" height={350}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="day"
                        label={{ value: 'Days', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        label={{ value: 'Count', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Legend
                        verticalAlign="top"
                        height={36}
                        wrapperStyle={{ paddingBottom: '10px' }}
                    />
                    <Line
                        type="monotone"
                        dataKey="Susceptible"
                        stroke="#2E7D32"
                        strokeWidth={2.5}
                        dot={false}
                    />
                    <Line
                        type="monotone"
                        dataKey="Exposed"
                        stroke="#FF9800"
                        strokeWidth={2.5}
                        dot={false}
                    />
                    <Line
                        type="monotone"
                        dataKey="Infected"
                        stroke="#D32F2F"
                        strokeWidth={2.5}
                        dot={false}
                    />
                    <Line
                        type="monotone"
                        dataKey="Recovered"
                        stroke="#1976D2"
                        strokeWidth={2.5}
                        dot={false}
                    />
                    <Line
                        type="monotone"
                        dataKey="Deceased"
                        stroke="#424242"
                        strokeWidth={2.5}
                        dot={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Daily New Cases Bar Chart (matching backend image)
export function DailyNewCasesBar({ history }) {
    if (!history || !history.I) return null

    // Calculate daily new infections
    const dailyNew = history.I.map((current, i) => {
        const prev = i > 0 ? history.I[i - 1] : 0
        return Math.max(0, current - prev)
    })

    const data = dailyNew.map((cases, i) => ({
        day: i,
        Cases: cases
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Daily New Cases</h3>
            <ResponsiveContainer width="100%" height={350}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="day"
                        label={{ value: 'Days', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        label={{ value: 'Cases', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Bar dataKey="Cases" fill="#D32F2F" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Integrated Risk Model (matching backend image)
export function IntegratedRiskModel({ simulationResults }) {
    if (!simulationResults?.history) return null

    const { history, detailed_data } = simulationResults
    const totalPopulation = history.S[0] + history.I[0] + history.R[0]
    const lastDay = history.S.length - 1
    const peakInfections = Math.max(...history.I)
    const totalDeaths = history.D?.[lastDay] || 0
    const attackRate = ((history.R[lastDay] + totalDeaths) / totalPopulation * 100).toFixed(1)

    // Calculate risk score (0-1)
    const riskScore = Math.min(1, (peakInfections / totalPopulation + totalDeaths / totalPopulation + parseFloat(attackRate) / 100) / 3)

    const data = [
        { name: 'Low Risk', value: riskScore < 0.3 ? 1 : 0, fill: '#4CAF50' },
        { name: 'Medium Risk', value: riskScore >= 0.3 && riskScore < 0.7 ? 1 : 0, fill: '#FF9800' },
        { name: 'High Risk', value: riskScore >= 0.7 ? 1 : 0, fill: '#000000' }
    ].filter(d => d.value > 0)

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Integrated Risk Model</h3>
            <ResponsiveContainer width="100%" height={350}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 text-center">
                <p className="text-lg font-semibold">
                    Risk Score: <span className={riskScore >= 0.7 ? 'text-red-600' : riskScore >= 0.3 ? 'text-orange-600' : 'text-green-600'}>
                        {(riskScore * 100).toFixed(1)}%
                    </span>
                </p>
            </div>
        </div>
    )
}

// NEW: Age Distribution of Infections Bar Chart (matching backend image)
export function AgeDistributionInfections({ ageData }) {
    if (!ageData || !ageData.bins || !ageData.counts) return null

    const data = ageData.counts.map((count, i) => ({
        age: `${ageData.bins[i]}-${ageData.bins[i + 1] || '+'}`,
        Infections: count
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Age Distribution of Infections</h3>
            <ResponsiveContainer width="100%" height={350}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="age"
                        label={{ value: 'Age', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        label={{ value: 'Count', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Bar dataKey="Infections" fill="#D32F2F" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Network and Demographic Metrics - Degree Distribution Bar
export function DegreeDistributionBar({ degreeData }) {
    if (!degreeData || !degreeData.bins || !degreeData.counts) return null

    const data = degreeData.counts.map((count, i) => ({
        degree: Math.round(degreeData.bins[i]),
        Frequency: count
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Degree Distribution</h3>
            <ResponsiveContainer width="100%" height={350}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="degree"
                        label={{ value: 'Degree', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        label={{ value: 'Frequency', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Bar dataKey="Frequency" fill="#5C6BC0" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Network and Demographic Metrics - Age Distribution Bar
export function AgeDistributionBarGreen({ ageData }) {
    if (!ageData || !ageData.bins || !ageData.counts) return null

    const data = ageData.counts.map((count, i) => ({
        age: Math.round(ageData.bins[i]),
        Frequency: count
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Age Distribution</h3>
            <ResponsiveContainer width="100%" height={350}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="age"
                        label={{ value: 'Age', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        label={{ value: 'Frequency', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Bar dataKey="Frequency" fill="#66BB6A" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Network and Demographic Metrics - Mobility Distribution Pie
export function MobilityDistributionPie({ mobilityData }) {
    if (!mobilityData || !mobilityData.bins || !mobilityData.counts) return null

    const data = mobilityData.counts.map((count, i) => ({
        name: `${mobilityData.bins[i].toFixed(1)}-${mobilityData.bins[i + 1]?.toFixed(1) || '1.0'}`,
        value: count
    })).filter(d => d.value > 0)

    const COLORS_MOBILITY = ['#FFB74D', '#FFA726', '#FF9800', '#FB8C00', '#F57C00', '#EF6C00', '#E65100']

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Mobility Distribution</h3>
            <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS_MOBILITY[index % COLORS_MOBILITY.length]} />
                        ))}
                    </Pie>
                    <Tooltip />
                </PieChart>
            </ResponsiveContainer>
        </div>
    )
}

// NEW: Network and Demographic Metrics - Social Clustering Pie
export function SocialClusteringPie({ clusteringData }) {
    if (!clusteringData || !clusteringData.age_groups || !clusteringData.clustering) return null

    const data = clusteringData.age_groups.map((group, i) => ({
        name: group,
        value: clusteringData.clustering[i]
    }))

    const COLORS_PURPLE = ['#9C27B0', '#8E24AA', '#7B1FA2', '#6A1B9A', '#4A148C']

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-center text-white">Social Clustering by Age</h3>
            <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS_PURPLE[index % COLORS_PURPLE.length]} />
                        ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                </PieChart>
            </ResponsiveContainer>
        </div>
    )
}

// 1. SEIR Dynamics with Multiple Lines
export function SEIRDynamicsChart({ history }) {
    if (!history || !history.S) return null

    const data = history.S.map((s, i) => ({
        day: i,
        Susceptible: s,
        Exposed: history.E?.[i] || 0,
        Infected: history.I[i],
        Recovered: history.R[i],
        Deceased: history.D?.[i] || 0
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">📈 SEIR Dynamics</h3>
            <ResponsiveContainer width="100%" height={400}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Population', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="Susceptible" stroke={COLORS.susceptible} strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Exposed" stroke={COLORS.exposed} strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Infected" stroke={COLORS.infected} strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Recovered" stroke={COLORS.recovered} strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Deceased" stroke={COLORS.deceased} strokeWidth={2} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    )
}

// 2. Daily New Cases with 7-Day Average
export function DailyNewInfectionsChart({ dailyCases }) {
    if (!dailyCases || dailyCases.length === 0) return null

    const calculateMovingAvg = (data, window = 7) => {
        return data.map((_, i) => {
            const start = Math.max(0, i - window + 1)
            const slice = data.slice(start, i + 1)
            return slice.reduce((a, b) => a + b, 0) / slice.length
        })
    }

    const movingAvg = calculateMovingAvg(dailyCases)

    const data = dailyCases.map((cases, i) => ({
        day: i,
        'Daily Cases': cases,
        '7-Day Average': movingAvg[i]
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">📊 Daily New Infections</h3>
            <ResponsiveContainer width="100%" height={400}>
                <ComposedChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'New Cases', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Daily Cases" fill="#F44336" opacity={0.6} />
                    <Line type="monotone" dataKey="7-Day Average" stroke="#8B0000" strokeWidth={3} dot={false} />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    )
}

// 3. Stacked Area Chart for Disease States
export function StackedAreaChart({ history }) {
    if (!history || !history.S) return null

    const data = history.S.map((s, i) => ({
        day: i,
        Susceptible: s,
        Infected: history.I[i],
        Recovered: history.R[i],
        Deceased: history.D?.[i] || 0
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">🔺 Stacked Population States</h3>
            <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Population', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="Susceptible" stackId="1" stroke={COLORS.susceptible} fill={COLORS.susceptible} fillOpacity={0.8} />
                    <Area type="monotone" dataKey="Infected" stackId="1" stroke={COLORS.infected} fill={COLORS.infected} fillOpacity={0.8} />
                    <Area type="monotone" dataKey="Recovered" stackId="1" stroke={COLORS.recovered} fill={COLORS.recovered} fillOpacity={0.8} />
                    <Area type="monotone" dataKey="Deceased" stackId="1" stroke={COLORS.deceased} fill={COLORS.deceased} fillOpacity={0.8} />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    )
}

// 4. Healthcare System Burden with Severity Levels
export function SeverityBreakdownChart({ severityData }) {
    if (!severityData || !severityData.hospitalized) return null

    const data = severityData.hospitalized.map((_, i) => ({
        day: i,
        Asymptomatic: severityData.asymptomatic[i],
        Mild: severityData.mild[i],
        Severe: severityData.severe[i],
        Hospitalized: severityData.hospitalized[i],
        Critical: severityData.critical[i]
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">🏥 Healthcare System Burden</h3>
            <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Patients', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="Asymptomatic" stackId="1" stroke="#FFE4E1" fill="#FFE4E1" />
                    <Area type="monotone" dataKey="Mild" stackId="1" stroke="#FFB6C1" fill="#FFB6C1" />
                    <Area type="monotone" dataKey="Severe" stackId="1" stroke="#FF6B6B" fill="#FF6B6B" />
                    <Area type="monotone" dataKey="Hospitalized" stackId="1" stroke="#DC143C" fill="#DC143C" />
                    <Area type="monotone" dataKey="Critical" stackId="1" stroke="#8B0000" fill="#8B0000" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    )
}

// 5. Age Distribution Pie Chart
export function AgeDistributionPie({ ageData }) {
    if (!ageData || !ageData.bins || !ageData.counts) return null

    const data = ageData.counts.map((count, i) => ({
        name: `${ageData.bins[i]}-${ageData.bins[i + 1] || '+'}`,
        value: count
    })).filter(d => d.value > 0)

    const COLORS_PIE = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739']

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">🎂 Age Distribution of Infections</h3>
            <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS_PIE[index % COLORS_PIE.length]} />
                        ))}
                    </Pie>
                    <Tooltip />
                </PieChart>
            </ResponsiveContainer>
        </div>
    )
}

// 6. Age Distribution Bar Chart
export function AgeDistributionBar({ ageData }) {
    if (!ageData || !ageData.bins || !ageData.counts) return null

    const data = ageData.counts.map((count, i) => ({
        age: `${ageData.bins[i]}-${ageData.bins[i + 1] || '+'}`,
        count: count
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">📊 Age Distribution (Bar)</h3>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="age" label={{ value: 'Age Group', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#F44336" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// 7. Network Degree Distribution
export function DegreeDistributionChart({ degreeData }) {
    if (!degreeData || !degreeData.bins || !degreeData.counts) return null

    const data = degreeData.counts.map((count, i) => ({
        degree: Math.round(degreeData.bins[i]),
        frequency: count
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">🌐 Network Degree Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="degree" label={{ value: 'Degree (Connections)', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Frequency', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Bar dataKey="frequency" fill="#2196F3" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// 8. R-Effective Over Time
export function REffectiveChart({ rEffectiveHistory }) {
    if (!rEffectiveHistory || rEffectiveHistory.length === 0) return null

    const data = rEffectiveHistory.map((r, i) => ({
        day: i,
        'R-Effective': r
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">📉 R-Effective Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'R-Effective', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Line type="monotone" dataKey="R-Effective" stroke="#9C27B0" strokeWidth={3} dot={false} />
                    {/* R=1 threshold line */}
                    <Line y={1} stroke="#FF0000" strokeDasharray="5 5" />
                </LineChart>
            </ResponsiveContainer>
            <p className="text-sm text-gray-300 mt-2">Red dashed line indicates R=1 (epidemic control threshold)</p>
        </div>
    )
}

// 9. Cumulative Statistics Comparison
export function CumulativeStatsChart({ history }) {
    if (!history || !history.S) return null

    const data = history.S.map((_, i) => {
        const totalRecovered = history.R[i]
        const totalDeaths = history.D?.[i] || 0
        const totalInfected = (history.S[0] - history.S[i]) // Total who left susceptible pool

        return {
            day: i,
            'Total Infected': totalInfected,
            'Total Recovered': totalRecovered,
            'Total Deaths': totalDeaths
        }
    })

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">📈 Cumulative Statistics</h3>
            <ResponsiveContainer width="100%" height={350}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Cumulative Count', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="Total Infected" stroke="#F44336" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Total Recovered" stroke="#2196F3" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="Total Deaths" stroke="#757575" strokeWidth={2} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    )
}

// 10. Attack Rate by Day
export function AttackRateChart({ history }) {
    if (!history || !history.S) return null

    const initialPop = history.S[0]
    const data = history.S.map((s, i) => ({
        day: i,
        'Attack Rate (%)': ((initialPop - s) / initialPop) * 100
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">🎯 Attack Rate Progression</h3>
            <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Attack Rate (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Area type="monotone" dataKey="Attack Rate (%)" stroke="#FF9800" fill="#FF9800" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    )
}

// 11. Active vs Recovered Comparison
export function ActiveVsRecoveredChart({ history }) {
    if (!history || !history.I) return null

    const data = history.I.map((infected, i) => ({
        day: i,
        Active: infected,
        Recovered: history.R[i],
        Deaths: history.D?.[i] || 0
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">⚖️ Active vs Recovered vs Deaths</h3>
            <ResponsiveContainer width="100%" height={350}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Active" fill="#F44336" />
                    <Bar dataKey="Recovered" fill="#2196F3" />
                    <Bar dataKey="Deaths" fill="#757575" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// 12. Infection Rate Heatmap Data (for display)
export function InfectionRateIndicator({ dailyCases }) {
    if (!dailyCases || dailyCases.length < 7) return null

    const lastWeek = dailyCases.slice(-7)
    const avgLastWeek = lastWeek.reduce((a, b) => a + b, 0) / 7
    const prevWeek = dailyCases.slice(-14, -7)
    const avgPrevWeek = prevWeek.reduce((a, b) => a + b, 0) / 7

    const trend = avgPrevWeek > 0 ? ((avgLastWeek - avgPrevWeek) / avgPrevWeek) * 100 : 0
    const trendColor = trend > 10 ? 'bg-red-500' : trend > 0 ? 'bg-orange-500' : trend > -10 ? 'bg-yellow-500' : 'bg-green-500'

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Weekly Trend Indicator</h3>
            <div className="flex items-center justify-center">
                <div className={`${trendColor} text-white rounded-lg p-8 text-center`}>
                    <div className="text-4xl font-bold">
                        {trend > 0 ? '+' : ''}{trend.toFixed(1)}%
                    </div>
                    <div className="text-lg mt-2">
                        {trend > 10 ? 'Rapid Increase' : trend > 0 ? 'Increasing' : trend > -10 ? 'Stable' : 'Decreasing'}
                    </div>
                    <div className="text-sm mt-4">
                        Week avg: {avgLastWeek.toFixed(1)} cases/day
                    </div>
                </div>
            </div>
        </div>
    )
}

// 13. Mobility Distribution Chart (Backend-matching) - CHANGED TO RADIAL BAR
export function MobilityDistributionChart({ mobilityData }) {
    if (!mobilityData || !mobilityData.bins || !mobilityData.counts) return null

    const data = mobilityData.counts.map((count, i) => ({
        name: `${mobilityData.bins[i].toFixed(1)}`,
        value: count,
        fill: `hsl(${30 + i * 10}, 70%, 50%)`
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Mobility Distribution (Radial)</h3>
            <ResponsiveContainer width="100%" height={350}>
                <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="10%"
                    outerRadius="80%"
                    data={data}
                    startAngle={180}
                    endAngle={0}
                >
                    <PolarGrid />
                    <RadialBar
                        minAngle={15}
                        label={{ position: 'insideStart', fill: '#fff', angle: 0 }}
                        background
                        clockWise
                        dataKey="value"
                    />
                    <Legend iconSize={10} layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ paddingTop: '20px' }} />
                    <Tooltip />
                </RadialBarChart>
            </ResponsiveContainer>
        </div>
    )
}

// 14. Social Clustering by Age Chart (Backend-matching) - CHANGED TO RADAR
export function SocialClusteringChart({ clusteringData }) {
    if (!clusteringData || !clusteringData.age_groups || !clusteringData.clustering) return null

    const data = clusteringData.age_groups.map((group, i) => ({
        age_group: group,
        clustering: clusteringData.clustering[i],
        fullMark: 1.0
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Social Clustering by Age (Radar)</h3>
            <ResponsiveContainer width="100%" height={350}>
                <RadarChart data={data}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="age_group" />
                    <PolarRadiusAxis angle={90} domain={[0, 1]} />
                    <Radar name="Clustering Coefficient" dataKey="clustering" stroke="#9C27B0" fill="#9C27B0" fillOpacity={0.6} />
                    <Tooltip />
                    <Legend />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    )
}

// 15. Hospital Capacity Timeline Chart (Backend-matching)
export function HospitalCapacityChart({ hospitalData, capacity }) {
    if (!hospitalData || !hospitalData.hospitalized || !hospitalData.critical) return null

    const data = hospitalData.hospitalized.map((hosp, i) => ({
        day: i,
        Hospitalized: hosp,
        Critical: hospitalData.critical[i],
        Capacity: capacity
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Hospital Bed Usage Over Time</h3>
            <ResponsiveContainer width="100%" height={350}>
                <ComposedChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Beds', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="Hospitalized" stackId="1" stroke="#800080" fill="#800080" />
                    <Area type="monotone" dataKey="Critical" stackId="1" stroke="#000000" fill="#000000" />
                    <Line type="monotone" dataKey="Capacity" stroke="#FF0000" strokeWidth={3} strokeDasharray="5 5" />
                </ComposedChart>
            </ResponsiveContainer>
            <p className="text-sm text-gray-300 mt-2">Red dashed line indicates hospital capacity</p>
        </div>
    )
}

// 16. Infection Timeline Heatmap-style Chart
export function InfectionWaveChart({ history }) {
    if (!history || !history.I) return null

    // Calculate daily changes in infections
    const data = history.I.map((current, i) => {
        const prev = i > 0 ? history.I[i - 1] : 0
        const change = current - prev
        return {
            day: i,
            Active: current,
            Change: change,
            color: change > 0 ? '#FF4444' : change < 0 ? '#44FF44' : '#FFAA00'
        }
    })

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Infection Wave Analysis</h3>
            <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="Active" stroke="#F44336" strokeWidth={2} dot={false} />
                    <Bar dataKey="Change" fill="#4CAF50" opacity={0.5} />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    )
}

// 17. NEW: Population State Treemap
export function PopulationStateTreemap({ history }) {
    if (!history || !history.S) return null

    const lastDay = history.S.length - 1

    // Treemap needs hierarchical data structure
    const total = history.S[lastDay] + history.I[lastDay] + history.R[lastDay] + (history.D?.[lastDay] || 0)

    const data = {
        name: 'Population',
        children: [
            {
                name: 'Susceptible',
                size: history.S[lastDay],
                fill: '#4CAF50'
            },
            {
                name: 'Infected',
                size: history.I[lastDay],
                fill: '#F44336'
            },
            {
                name: 'Recovered',
                size: history.R[lastDay],
                fill: '#2196F3'
            },
            {
                name: 'Deceased',
                size: history.D?.[lastDay] || 1,
                fill: '#757575'
            }
        ].filter(d => d.size > 0)
    }

    const COLORS = ['#4CAF50', '#F44336', '#2196F3', '#757575']

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Population Distribution (Treemap)</h3>
            <ResponsiveContainer width="100%" height={350}>
                <Treemap
                    data={data.children}
                    dataKey="size"
                    ratio={4 / 3}
                    stroke="#fff"
                    fill="#8884d8"
                >
                    {data.children.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                </Treemap>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                {data.children.map((item, i) => (
                    <div key={i} className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded" style={{ backgroundColor: item.fill }}></div>
                        <span>{item.name}: {item.size.toLocaleString()} ({((item.size / total) * 100).toFixed(1)}%)</span>
                    </div>
                ))}
            </div>
        </div>
    )
}

// 18. NEW: Age vs Infection Risk Scatter Plot
export function AgeInfectionScatter({ ageData, degreeData }) {
    if (!ageData || !degreeData || !ageData.counts || !degreeData.counts) return null

    const data = []
    const minLength = Math.min(ageData.counts.length, degreeData.counts.length)

    for (let i = 0; i < minLength; i++) {
        if (ageData.counts[i] > 0) {
            data.push({
                age: ageData.bins[i],
                infections: ageData.counts[i],
                connections: degreeData.bins[i] || 0,
                z: ageData.counts[i] * 2
            })
        }
    }

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Age vs Infections (Scatter)</h3>
            <ResponsiveContainer width="100%" height={350}>
                <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        type="number"
                        dataKey="age"
                        name="Age"
                        label={{ value: 'Age', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis
                        type="number"
                        dataKey="infections"
                        name="Infections"
                        label={{ value: 'Infections', angle: -90, position: 'insideLeft' }}
                    />
                    <ZAxis type="number" dataKey="z" range={[50, 400]} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    <Scatter name="Age vs Infections" data={data} fill="#FF5722" />
                </ScatterChart>
            </ResponsiveContainer>
        </div>
    )
}

// 19. NEW: Degree Distribution Radial Bar
export function DegreeDistributionRadial({ degreeData }) {
    if (!degreeData || !degreeData.bins || !degreeData.counts) return null

    const data = degreeData.counts.slice(0, 10).map((count, i) => ({
        name: `${Math.round(degreeData.bins[i])}-${Math.round(degreeData.bins[i + 1])}`,
        value: count,
        fill: `hsl(${200 + i * 15}, 70%, 50%)`
    }))

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">Network Degree (Radial)</h3>
            <ResponsiveContainer width="100%" height={350}>
                <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="20%"
                    outerRadius="90%"
                    data={data}
                    startAngle={90}
                    endAngle={450}
                >
                    <PolarGrid />
                    <RadialBar
                        minAngle={15}
                        label={{ fill: '#666', position: 'insideStart' }}
                        background
                        clockWise
                        dataKey="value"
                    />
                    <Tooltip />
                </RadialBarChart>
            </ResponsiveContainer>
        </div>
    )
}
