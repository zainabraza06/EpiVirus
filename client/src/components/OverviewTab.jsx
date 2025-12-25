// components/OverviewTab.jsx
import { useState } from 'react'

export default function OverviewTab({
    simulator,
    animationReady,
    simulationHistory,
    simulationComplete,
    animationFrames,
    onRunExample,
    onPrepareAnimation,
    onNewSimulation
}) {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="text-center py-8">
                <h1 className="text-5xl font-bold mb-4 text-white">
                    🦠 EpiVirus
                </h1>
                <p className="text-xl text-gray-300">
                    Pandemic Simulation Platform
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Welcome Section */}
                    <div className="bg-gray-800 rounded-lg shadow-xl p-8">
                        <h2 className="text-3xl font-bold mb-6 text-white">
                            Welcome to the Pandemic Simulator
                        </h2>

                        <div className="prose max-w-none">
                            <h3 className="text-xl font-semibold text-gray-300 mt-4">🔑 Key Features:</h3>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                <div className="bg-blue-900 bg-opacity-40 p-4 rounded-lg">
                                    <h4 className="font-bold text-blue-300">🎯 Network Animation</h4>
                                    <ul className="text-sm text-gray-300 mt-2 space-y-1">
                                        <li>• Real-time disease spread visualization</li>
                                        <li>• Color-coded infection status</li>
                                        <li>• Animated transmission paths</li>
                                    </ul>
                                </div>

                                <div className="bg-green-900 bg-opacity-40 p-4 rounded-lg">
                                    <h4 className="font-bold text-green-300">🌐 Advanced Networks</h4>
                                    <ul className="text-sm text-gray-300 mt-2 space-y-1">
                                        <li>• Multiple network types</li>
                                        <li>• Hybrid multilayer structures</li>
                                        <li>• Custom community structures</li>
                                    </ul>
                                </div>

                                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                                    <h4 className="font-bold text-red-300 text-lg mb-3 flex items-center gap-2">
                                        <span className="text-2xl">🦠</span>
                                        <span>Disease Modeling</span>
                                    </h4>
                                    <ul className="text-sm text-gray-300 space-y-2">
                                        <li className="flex items-start gap-2">
                                            <span className="text-red-500 font-bold">•</span>
                                            <span>Multiple COVID-19 variants</span>
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <span className="text-red-500 font-bold">•</span>
                                            <span>Custom disease parameters</span>
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <span className="text-red-500 font-bold">•</span>
                                            <span>Age-stratified severity</span>
                                        </li>
                                    </ul>
                                </div>

                                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                                    <h4 className="font-bold text-purple-300 text-lg mb-3 flex items-center gap-2">
                                        <span className="text-2xl">🛡️</span>
                                        <span>Interventions</span>
                                    </h4>
                                    <ul className="text-sm text-gray-300 space-y-2">
                                        <li className="flex items-start gap-2">
                                            <span className="text-purple-500 font-bold">•</span>
                                            <span>Mask mandates & distancing</span>
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <span className="text-purple-500 font-bold">•</span>
                                            <span>Vaccination campaigns</span>
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <span className="text-purple-500 font-bold">•</span>
                                            <span>Lockdown strategies</span>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>

                        {/* Configuration Status */}
                        <div className="mt-8">
                            <h3 className="text-xl font-semibold text-gray-300 mb-4">⚙️ Configuration Status</h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <StatusCard
                                    label="Simulator"
                                    status={simulator ? 'ready' : 'not-configured'}
                                />
                                <StatusCard
                                    label="Animation"
                                    status={animationReady ? 'ready' : 'not-ready'}
                                />
                                <StatusCard
                                    label="Results"
                                    status={simulationHistory ? 'available' : 'not-available'}
                                />
                                <StatusCard
                                    label="Completion"
                                    status={simulationComplete ? 'complete' : 'pending'}
                                />
                            </div>
                        </div>

                        {/* Simulation Results Quick View */}
                        {simulationHistory && simulationHistory.history && (
                            <div className="mt-8 bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl">
                                <h3 className="text-xl font-semibold text-white mb-4">📊 Latest Simulation Results</h3>
                                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                                    <div className="bg-gray-700 p-4 rounded-xl text-center border border-gray-600">
                                        <div className="text-green-400 text-2xl mb-1">😊</div>
                                        <div className="text-xs text-gray-400 mb-1">Final Susceptible</div>
                                        <div className="text-xl font-bold text-white">
                                            {Math.round(simulationHistory.history.S[simulationHistory.history.S.length - 1] || 0)}
                                        </div>
                                    </div>

                                    <div className="bg-gray-700 p-4 rounded-xl text-center border border-gray-600">
                                        <div className="text-yellow-400 text-2xl mb-1">🌥️</div>
                                        <div className="text-xs text-gray-400 mb-1">Peak Exposed</div>
                                        <div className="text-xl font-bold text-white">
                                            {Math.round(Math.max(...(simulationHistory.history.E || [0])))}
                                        </div>
                                    </div>

                                    <div className="bg-gray-700 p-4 rounded-xl text-center border border-gray-600">
                                        <div className="text-red-400 text-2xl mb-1">🦠</div>
                                        <div className="text-xs text-gray-400 mb-1">Peak Infected</div>
                                        <div className="text-xl font-bold text-white">
                                            {Math.round(Math.max(...(simulationHistory.history.I || [0])))}
                                        </div>
                                    </div>

                                    <div className="bg-gray-700 p-4 rounded-xl text-center border border-gray-600">
                                        <div className="text-blue-400 text-2xl mb-1">💙</div>
                                        <div className="text-xs text-gray-400 mb-1">Total Recovered</div>
                                        <div className="text-xl font-bold text-white">
                                            {Math.round(simulationHistory.history.R[simulationHistory.history.R.length - 1] || 0)}
                                        </div>
                                    </div>

                                    <div className={`bg-gray-700 p-4 rounded-xl text-center border-2 ${(simulationHistory.summary?.total_deaths ?? (simulationHistory.history.D?.[simulationHistory.history.D.length - 1] || 0)) > 0 ? 'border-red-600' : 'border-green-600'}`}>
                                        <div className={`text-2xl mb-1 ${(simulationHistory.summary?.total_deaths ?? (simulationHistory.history.D?.[simulationHistory.history.D.length - 1] || 0)) > 0 ? 'text-red-500' : 'text-green-500'}`}>
                                            {(simulationHistory.summary?.total_deaths ?? (simulationHistory.history.D?.[simulationHistory.history.D.length - 1] || 0)) > 0 ? '💀' : '✓'}
                                        </div>
                                        <div className="text-xs text-gray-400 mb-1">Total Deaths</div>
                                        <div className={`text-xl font-bold ${(simulationHistory.summary?.total_deaths ?? (simulationHistory.history.D?.[simulationHistory.history.D.length - 1] || 0)) > 0 ? 'text-red-400' : 'text-green-400'}`}>
                                            {Math.round(simulationHistory.summary?.total_deaths ?? (simulationHistory.history.D?.[simulationHistory.history.D.length - 1] || 0))}
                                        </div>
                                        {(simulationHistory.summary?.total_deaths ?? (simulationHistory.history.D?.[simulationHistory.history.D.length - 1] || 0)) === 0 && (
                                            <div className="text-xs text-green-400 mt-1">Zero fatalities!</div>
                                        )}
                                    </div>
                                </div>
                                <div className="bg-gray-700 p-4 rounded-xl text-center border border-gray-600">
                                    <div className="text-purple-400 text-2xl mb-1">🔢</div>
                                    <div className="text-xs text-gray-400 mb-1">R Effective</div>
                                    <div className="text-xl font-bold text-white">
                                        {(simulationHistory.summary?.final_r_effective || 0).toFixed(2)}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Quick Start Guide */}
                        <div className="mt-8 bg-gray-800 p-8 rounded-2xl border border-gray-700 shadow-xl">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="bg-gray-700 p-3 rounded-xl shadow-lg">
                                    <span className="text-2xl">🚀</span>
                                </div>
                                <h3 className="text-2xl font-bold text-white">Quick Start Guide</h3>
                            </div>
                            <ol className="space-y-3 text-gray-300">
                                <li className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-600">
                                    <span className="flex-shrink-0 w-8 h-8 bg-gray-700 text-white rounded-full flex items-center justify-center font-bold">1</span>
                                    <span className="flex-1 pt-1">Go to <strong>Simulation</strong> tab</span>
                                </li>
                                <li className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                                    <span className="flex-shrink-0 w-8 h-8 bg-gray-700 text-white rounded-full flex items-center justify-center font-bold">2</span>
                                    <span className="flex-1 pt-1">Configure parameters (network, disease, interventions)</span>
                                </li>
                                <li className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                                    <span className="flex-shrink-0 w-8 h-8 bg-gray-700 text-white rounded-full flex items-center justify-center font-bold">3</span>
                                    <span className="flex-1 pt-1">Review configuration summary</span>
                                </li>
                                <li className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                                    <span className="flex-shrink-0 w-8 h-8 bg-gray-700 text-white rounded-full flex items-center justify-center font-bold">4</span>
                                    <span className="flex-1 pt-1">Run simulation</span>
                                </li>
                                <li className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                                    <span className="flex-shrink-0 w-8 h-8 bg-gray-700 text-white rounded-full flex items-center justify-center font-bold">5</span>
                                    <span className="flex-1 pt-1">Watch animation in <strong>Visualization</strong> tab</span>
                                </li>
                                <li className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                                    <span className="flex-shrink-0 w-8 h-8 bg-gray-700 text-white rounded-full flex items-center justify-center font-bold">6</span>
                                    <span className="flex-1 pt-1">Analyze results in <strong>Analysis</strong> tab</span>
                                </li>
                                <li className="flex items-start gap-3 p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                                    <span className="flex-shrink-0 w-8 h-8 bg-gray-700 text-white rounded-full flex items-center justify-center font-bold">7</span>
                                    <span className="flex-1 pt-1">Export data in <strong>Results</strong> tab</span>
                                </li>
                            </ol>
                            <div className="mt-6 p-4 bg-gray-700 rounded-xl shadow-md border-l-4 border-indigo-500">
                                <p className="text-sm text-indigo-300 font-semibold flex items-center gap-2">
                                    <span className="text-lg">💡</span>
                                    <span>Pro tip: Start with example simulation to see all features!</span>
                                </p>
                            </div>
                        </div>

                        {/* Animation Preview */}
                        {animationReady && animationFrames && animationFrames.length > 0 && (
                            <div className="mt-8">
                                <h3 className="text-xl font-semibold text-gray-300 mb-4">🎬 Current Animation Preview</h3>
                                <div className="bg-gray-700 p-4 rounded-lg">
                                    <p className="text-center text-gray-400">
                                        {animationFrames.length} frames available
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Feature Highlights */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <FeatureCard
                            icon="🌐"
                            title="Network Types"
                            description="Simulate realistic social structures including households, workplaces, and schools."
                        />
                        <FeatureCard
                            icon="🦠"
                            title="Disease Variants"
                            description="Model different COVID-19 variants with varying transmission and mortality rates."
                        />
                        <FeatureCard
                            icon="🛡️"
                            title="Interventions"
                            description="Test lockdowns, vaccination programs, and other public health interventions."
                        />
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-8">
                    {/* Quick Actions */}
                    <div className="bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700">
                        <div className="flex items-center gap-2 mb-6">
                            <span className="text-2xl">🚀</span>
                            <h3 className="text-2xl font-bold text-white">Quick Actions</h3>
                        </div>

                        {!simulator && (
                            <div className="mb-6 p-4 bg-blue-900 bg-opacity-40 rounded-xl border-l-4 border-blue-500">
                                <p className="text-sm text-blue-700 font-semibold">
                                    👇 Start here to see the simulator in action!
                                </p>
                            </div>
                        )}

                        <div className="space-y-4">
                            <button
                                onClick={onRunExample}
                                className="w-full py-5 px-6 bg-indigo-600 text-white rounded-2xl font-bold text-lg hover:bg-indigo-700 transition-all shadow-xl hover:shadow-2xl transform hover:scale-105 flex items-center justify-center gap-3"
                            >
                                <span className="text-2xl">▶️</span>
                                <span>Run Example Simulation</span>
                            </button>

                            {simulator && !animationReady && simulationHistory && (
                                <button
                                    onClick={onPrepareAnimation}
                                    className="w-full py-5 px-6 bg-green-600 text-white rounded-2xl font-bold text-lg hover:bg-green-700 transition-all shadow-xl hover:shadow-2xl transform hover:scale-105 flex items-center justify-center gap-3"
                                >
                                    <span className="text-2xl">🎬</span>
                                    <span>Prepare Animation</span>
                                </button>
                            )}

                            {simulator && (
                                <button
                                    onClick={onNewSimulation}
                                    className="w-full py-4 px-6 bg-gray-700 text-white rounded-2xl font-semibold hover:bg-gray-600 transition-all shadow-lg hover:shadow-xl transform hover:scale-102 flex items-center justify-center gap-2"
                                >
                                    <span className="text-xl">🔄</span>
                                    <span>New Simulation</span>
                                </button>
                            )}
                        </div>
                    </div>

                    {/* State Legend */}
                    <div className="bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700">
                        <div className="flex items-center gap-2 mb-6">
                            <span className="text-2xl">🎨</span>
                            <h3 className="text-2xl font-bold text-white">State Colors</h3>
                        </div>
                        <div className="space-y-3">
                            <StateLegendItem color="#4CAF50" label="Susceptible" />
                            <StateLegendItem color="#FF9800" label="Exposed" />
                            <StateLegendItem color="#F44336" label="Infectious" />
                            <StateLegendItem color="#2196F3" label="Recovered" />
                            <StateLegendItem color="#757575" label="Deceased" />
                            <StateLegendItem color="#9C27B0" label="Vaccinated" />
                        </div>
                    </div>

                    {/* Tips */}
                    <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
                        <h3 className="text-xl font-semibold text-yellow-300 mb-4">💡 Tips</h3>
                        <ul className="space-y-2 text-sm text-gray-300">
                            <li>• Start with 500-1000 population for testing</li>
                            <li>• Try different network structures</li>
                            <li>• Compare intervention strategies</li>
                            <li>• Use custom parameters for research</li>
                            <li>• Export animations for presentations</li>
                        </ul>
                    </div>

                    {/* Navigation */}
                    <div className="bg-gray-800 rounded-lg shadow-xl p-6">
                        <h3 className="text-xl font-semibold text-white mb-4">🔍 Where to Go:</h3>
                        <div className="space-y-3">
                            <NavItem title="⚙️ Simulation" description="Configure all parameters" />
                            <NavItem title="📊 Analysis" description="Detailed epidemic analysis" />
                            <NavItem title="🎨 Visualization" description="Network visualization" />
                            <NavItem title="🎬 Animation" description="Create and export videos" />
                            <NavItem title="📈 Results" description="Download data and reports" />
                        </div>
                    </div>
                </div>
            </div>
        </div >
    )
}

function StatusCard({ label, status }) {
    const statusConfig = {
        'ready': { bg: 'bg-gray-800', border: 'border-green-700', text: 'text-green-300', icon: '✅', label: 'Ready', shadow: 'shadow-green-900' },
        'not-configured': { bg: 'from-gray-700 to-gray-800', border: 'border-gray-600', text: 'text-gray-400', icon: '⚙️', label: 'Not Set', shadow: 'shadow-gray-900' },
        'not-ready': { bg: 'bg-gray-800', border: 'border-yellow-700', text: 'text-yellow-300', icon: '⏳', label: 'Not Ready', shadow: 'shadow-yellow-900' },
        'not-available': { bg: 'from-gray-700 to-gray-800', border: 'border-gray-600', text: 'text-gray-400', icon: '📊', label: 'N/A', shadow: 'shadow-gray-900' },
        'available': { bg: 'bg-gray-800', border: 'border-blue-700', text: 'text-blue-300', icon: '✓', label: 'Available', shadow: 'shadow-blue-900' },
        'complete': { bg: 'bg-gray-800', border: 'border-purple-700', text: 'text-purple-300', icon: '✓', label: 'Complete', shadow: 'shadow-purple-900' },
        'pending': { bg: 'from-gray-700 to-gray-800', border: 'border-gray-600', text: 'text-gray-400', icon: '○', label: 'Pending', shadow: 'shadow-gray-900' }
    }

    const config = statusConfig[status] || statusConfig['not-configured']

    return (
        <div className={`bg-linear-to-br ${config.bg} p-6 rounded-2xl text-center border-2 ${config.border} shadow-lg ${config.shadow} hover:shadow-xl transform hover:scale-105 transition-all duration-300`}>
            <div className="text-4xl mb-3">{config.icon}</div>
            <div className="font-bold text-base text-white mb-1">{label}</div>
            <div className={`text-sm font-semibold ${config.text}`}>{config.label}</div>
        </div>
    )
}

function FeatureCard({ icon, title, description }) {
    return (
        <div className="bg-gray-800 rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-gray-700 hover:border-indigo-600 card-hover">
            <div className="bg-gray-700 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <div className="text-5xl">{icon}</div>
            </div>
            <h3 className="text-xl font-bold text-white mb-3 text-center">{title}</h3>
            <p className="text-sm text-gray-300 text-center leading-relaxed">{description}</p>
        </div>
    )
}

function StateLegendItem({ color, label }) {
    return (
        <div className="flex items-center gap-3 p-3 bg-gray-700 rounded-xl hover:bg-gray-600 transition-colors border border-gray-600 hover:border-gray-500">
            <div
                className="w-6 h-6 rounded-full shadow-md"
                style={{ backgroundColor: color, boxShadow: `0 0 10px ${color}40` }}
            />
            <span className="text-sm font-semibold text-gray-200 flex-1">{label}</span>
            <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: color }}
            />
        </div>
    )
}

function NavItem({ title, description }) {
    return (
        <div className="border-l-4 border-blue-500 pl-3">
            <div className="font-semibold text-white">{title}</div>
            <div className="text-xs text-gray-400">{description}</div>
        </div>
    )
}
