// components/SimulationResults.jsx
export default function SimulationResults({ results }) {
    const summary = results.summary || {}

    const metrics = [
        {
            label: 'Attack Rate',
            value: `${((summary.attack_rate || 0) * 100).toFixed(1)}%`,
            icon: '🎯'
        },
        {
            label: 'Peak Infections',
            value: (summary.peak_infections || 0).toLocaleString(),
            icon: '📈'
        },
        {
            label: 'Total Deaths',
            value: (summary.total_deaths || 0).toLocaleString(),
            icon: '💀'
        },
        {
            label: 'Total Recovered',
            value: (summary.total_recovered || 0).toLocaleString(),
            icon: '💚'
        },
        {
            label: 'Peak Day',
            value: `Day ${summary.peak_day || 0}`,
            icon: '📅'
        },
        {
            label: 'R Effective',
            value: (summary.final_r_effective || 0).toFixed(2),
            icon: '🔢'
        },
    ]

    return (
        <div className="bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700">
            <div className="flex items-center gap-3 mb-8">
                <div className="bg-gray-700 p-3 rounded-xl shadow-lg">
                    <span className="text-2xl">📊</span>
                </div>
                <h3 className="text-3xl font-bold text-white">Simulation Results</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {metrics.map((metric, index) => (
                    <div
                        key={index}
                        className="bg-gray-700 rounded-2xl p-6 text-white shadow-xl hover:shadow-2xl border border-gray-600 hover:border-gray-500 transition-all duration-300"
                    >
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-4xl">{metric.icon}</span>
                            <span className="text-sm font-semibold text-gray-300 uppercase tracking-wide">{metric.label}</span>
                        </div>
                        <div className="text-4xl font-bold">{metric.value}</div>
                    </div>
                ))}
            </div>

            {/* Additional Stats */}
            <div className="mt-8 grid grid-cols-2 gap-6">
                <div className="bg-gray-800 rounded-2xl p-6 border-2 border-gray-600 shadow-lg hover:shadow-xl transition-all">
                    <div className="text-gray-300 font-semibold mb-2 flex items-center gap-2">
                        <span>🦠</span>
                        <span>Total Infected</span>
                    </div>
                    <div className="text-3xl font-bold text-white">
                        {(summary.total_infected || 0).toLocaleString()}
                    </div>
                </div>
                <div className="bg-gray-800 rounded-2xl p-6 border-2 border-gray-600 shadow-lg hover:shadow-xl transition-all">
                    <div className="text-gray-300 font-semibold mb-2 flex items-center gap-2">
                        <span>💉</span>
                        <span>Total Vaccinated</span>
                    </div>
                    <div className="text-3xl font-bold text-white">
                        {(summary.total_vaccinated || 0).toLocaleString()}
                    </div>
                </div>
            </div>
        </div>
    )
}
