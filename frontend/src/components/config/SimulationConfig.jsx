// components/SimulationConfig.jsx
import { useState } from 'react'
import AdvancedNetworkConfig from './AdvancedNetworkConfig'
import CustomDiseaseBuilder from './CustomDiseaseBuilder'
import AdvancedInterventionBuilder from './AdvancedInterventionBuilder'

export default function SimulationConfig({ diseases, networks, onStartSimulation, loading, currentStatus }) {
    const [config, setConfig] = useState({
        network: {
            population: 1000,
            network_type: 'hybrid',
            erdos_p: 0.01,
            watts_k: 8,
            watts_p: 0.3,
            barabasi_m: 3,
            block_intra: 0.15,
            block_inter: 0.01,
        },
        disease: {
            variant: 'omicron',
            custom_params: null
        },
        n_seed_infections: 10,
        seed_method: 'random',
        simulation_days: 120,
        intervention_scenario: 'no_intervention',
        vaccination_rate: 0.0,
        compliance_rate: 0.8,
        animate: true,
        animation_step: 2,
        custom_interventions: []
    })

    const [openAdvancedSection, setOpenAdvancedSection] = useState(null) // 'network', 'disease', or 'intervention'

    const handleNetworkChange = (field, value) => {
        setConfig(prev => ({
            ...prev,
            network: {
                ...prev.network,
                [field]: value
            }
        }))
    }

    const handleDiseaseChange = (field, value) => {
        setConfig(prev => ({
            ...prev,
            disease: {
                ...prev.disease,
                [field]: value
            }
        }))
    }

    const handleConfigChange = (field, value) => {
        setConfig(prev => ({
            ...prev,
            [field]: value
        }))
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        onStartSimulation(config)
    }

    const isRunning = currentStatus?.status === 'running'

    return (
        <div className="bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700">
            <div className="flex items-center gap-3 mb-8">
                <div className="bg-gray-700 p-4 rounded-xl shadow-lg">
                    <span className="text-3xl">⚙️</span>
                </div>
                <div>
                    <h2 className="text-3xl font-bold text-white">Simulation Configuration</h2>
                    <p className="text-gray-400 text-sm">Configure parameters for epidemic modeling</p>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Top Row - Primary Configuration */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* Network Configuration */}
                    <div className="bg-gray-700 bg-opacity-40 rounded-xl p-4 border border-gray-600">
                        <h3 className="text-lg font-bold text-white border-b border-indigo-500 pb-2 mb-3 flex items-center gap-2">
                            <span className="text-xl">🌐</span>
                            <span>Network</span>
                        </h3>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs font-medium text-gray-300 mb-1">Population</label>
                                <input
                                    type="number"
                                    value={config.network.population}
                                    onChange={(e) => handleNetworkChange('population', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm"
                                    min="100"
                                    max="10000"
                                    step="100"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-gray-300 mb-1">Network Type</label>
                                <select
                                    value={config.network.network_type}
                                    onChange={(e) => handleNetworkChange('network_type', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm"
                                >
                                    {networks.map(net => (
                                        <option key={net.id} value={net.id}>{net.name}</option>
                                    ))}
                                </select>
                                <p className="text-xs text-gray-400 mt-1">
                                    {networks.find(n => n.id === config.network.network_type)?.description}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Disease Configuration */}
                    <div className="bg-gray-700 bg-opacity-40 rounded-xl p-4 border border-gray-600">
                        <h3 className="text-lg font-bold text-white border-b border-red-500 pb-2 mb-3 flex items-center gap-2">
                            <span className="text-xl">🦠</span>
                            <span>Disease</span>
                        </h3>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs font-medium text-gray-300 mb-1">Variant</label>
                                <select
                                    value={config.disease.variant}
                                    onChange={(e) => handleDiseaseChange('variant', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all text-sm"
                                >
                                    {diseases.map(disease => (
                                        <option key={disease.id} value={disease.id}>{disease.name}</option>
                                    ))}
                                </select>
                                {diseases.length > 0 && (
                                    <div className="mt-2 p-2 bg-gray-800 rounded-lg text-xs text-gray-300 space-y-1">
                                        {(() => {
                                            const selected = diseases.find(d => d.id === config.disease.variant)
                                            return selected ? (
                                                <>
                                                    <div className="flex justify-between">
                                                        <span>R₀:</span>
                                                        <span className="font-semibold text-red-400">{selected.r0}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>Mortality:</span>
                                                        <span className="font-semibold text-red-400">{(selected.mortality_rate * 100).toFixed(1)}%</span>
                                                    </div>
                                                </>
                                            ) : null
                                        })()}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Infection Seeding */}
                    <div className="bg-gray-700 bg-opacity-40 rounded-xl p-4 border border-gray-600">
                        <h3 className="text-lg font-bold text-white border-b border-yellow-500 pb-2 mb-3 flex items-center gap-2">
                            <span className="text-xl">🎯</span>
                            <span>Seeding</span>
                        </h3>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs font-medium text-gray-300 mb-1">
                                    Initial Infections: <span className="text-yellow-400 font-semibold">{config.n_seed_infections}</span>
                                </label>
                                <input
                                    type="range"
                                    value={config.n_seed_infections}
                                    onChange={(e) => handleConfigChange('n_seed_infections', parseInt(e.target.value))}
                                    className="w-full accent-yellow-500"
                                    min="1"
                                    max="100"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-gray-300 mb-1">Seeding Method</label>
                                <select
                                    value={config.seed_method}
                                    onChange={(e) => handleConfigChange('seed_method', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent transition-all text-sm"
                                >
                                    <option value="random">Random</option>
                                    <option value="hubs">Network Hubs</option>
                                    <option value="mobile">High Mobility</option>
                                    <option value="geographic">Geographic</option>
                                    <option value="age_targeted">Age-Targeted</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Second Row - Simulation & Intervention Settings */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="bg-gray-700 bg-opacity-40 rounded-xl p-4 border border-gray-600">
                        <h3 className="text-lg font-bold text-white border-b border-purple-500 pb-2 mb-3 flex items-center gap-2">
                            <span className="text-xl">⚡</span>
                            <span>Simulation</span>
                        </h3>
                        <div>
                            <label className="block text-xs font-medium text-gray-300 mb-1">
                                Duration: <span className="text-purple-400 font-semibold">{config.simulation_days} days</span>
                            </label>
                            <input
                                type="range"
                                value={config.simulation_days}
                                onChange={(e) => handleConfigChange('simulation_days', parseInt(e.target.value))}
                                className="w-full accent-purple-500"
                                min="30"
                                max="365"
                                step="10"
                            />
                        </div>
                    </div>

                    <div className="bg-gray-700 bg-opacity-40 rounded-xl p-4 border border-gray-600">
                        <h3 className="text-lg font-bold text-white border-b border-green-500 pb-2 mb-3 flex items-center gap-2">
                            <span className="text-xl">🛡️</span>
                            <span>Intervention</span>
                        </h3>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs font-medium text-gray-300 mb-1">Scenario</label>
                                <select
                                    value={config.intervention_scenario}
                                    onChange={(e) => handleConfigChange('intervention_scenario', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-600 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all text-sm"
                                >
                                    <option value="no_intervention">No Intervention</option>
                                    <option value="rapid_response">Rapid Response</option>
                                    <option value="delayed_response">Delayed Response</option>
                                    <option value="herd_immunity">Herd Immunity</option>
                                </select>
                            </div>
                            {config.intervention_scenario !== 'no_intervention' && config.intervention_scenario !== 'herd_immunity' && (
                                <div>
                                    <label className="block text-xs font-medium text-gray-300 mb-1">
                                        Vaccination Rate: <span className="text-green-400 font-semibold">{(config.vaccination_rate * 100).toFixed(1)}%</span>
                                    </label>
                                    <input
                                        type="range"
                                        value={config.vaccination_rate}
                                        onChange={(e) => handleConfigChange('vaccination_rate', parseFloat(e.target.value))}
                                        className="w-full accent-green-500"
                                        min="0"
                                        max="0.05"
                                        step="0.001"
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Collapsible Advanced Options - Buttons Side by Side */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* Advanced Network Configuration */}
                    <button
                        type="button"
                        onClick={() => setOpenAdvancedSection(openAdvancedSection === 'network' ? null : 'network')}
                        className="w-full flex items-center justify-between bg-gray-700 hover:bg-gray-600 p-3 rounded-lg transition-all border border-gray-600"
                    >
                        <span className="font-semibold text-indigo-300 text-sm">🌐 Advanced Network</span>
                        <span className="text-indigo-400 text-sm">{openAdvancedSection === 'network' ? '▲' : '▼'}</span>
                    </button>

                    {/* Custom Disease Builder */}
                    <button
                        type="button"
                        onClick={() => setOpenAdvancedSection(openAdvancedSection === 'disease' ? null : 'disease')}
                        className="w-full flex items-center justify-between bg-gray-700 hover:bg-gray-600 p-3 rounded-lg transition-all border border-gray-600"
                    >
                        <span className="font-semibold text-red-300 text-sm">🦠 Custom Disease</span>
                        <span className="text-red-400 text-sm">{openAdvancedSection === 'disease' ? '▲' : '▼'}</span>
                    </button>

                    {/* Advanced Intervention Builder */}
                    <button
                        type="button"
                        onClick={() => setOpenAdvancedSection(openAdvancedSection === 'intervention' ? null : 'intervention')}
                        className="w-full flex items-center justify-between bg-gray-700 hover:bg-gray-600 p-3 rounded-lg transition-all border border-gray-600"
                    >
                        <span className="font-semibold text-green-300 text-sm">🛡️ Advanced Interventions</span>
                        <span className="text-green-400 text-sm">{openAdvancedSection === 'intervention' ? '▲' : '▼'}</span>
                    </button>
                </div>

                {/* Advanced Section Content - Full Width */}
                {openAdvancedSection === 'network' && (
                    <div className="mt-4">
                        <AdvancedNetworkConfig
                            networkType={config.network.network_type}
                            onParamsChange={(params) => {
                                setConfig(prev => ({
                                    ...prev,
                                    network: { ...prev.network, ...params }
                                }))
                            }}
                            initialParams={config.network}
                        />
                    </div>
                )}

                {openAdvancedSection === 'disease' && (
                    <div className="mt-4">
                        <CustomDiseaseBuilder
                            onParamsChange={(params) => {
                                handleDiseaseChange('custom_params', params)
                            }}
                            initialParams={config.disease.custom_params || {}}
                        />
                    </div>
                )}

                {openAdvancedSection === 'intervention' && (
                    <div className="mt-4">
                        <AdvancedInterventionBuilder
                            onInterventionsChange={(interventions) => {
                                handleConfigChange('custom_interventions', interventions)
                            }}
                            initialInterventions={config.custom_interventions}
                        />
                    </div>
                )}

                {/* Configuration Summary and Run Button */}
                <div className="flex items-center justify-between gap-4 bg-gray-800 p-4 rounded-lg border border-gray-700">
                    <div className="flex items-center gap-6 flex-wrap text-base text-gray-300">
                        <div className="flex items-center gap-1.5">
                            <span className="text-gray-400">Population:</span>
                            <span className="font-semibold text-white">{config.network.population}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <span className="text-gray-400">Network:</span>
                            <span className="font-semibold text-white">{config.network.network_type}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <span className="text-gray-400">Disease:</span>
                            <span className="font-semibold text-white">{config.disease.variant}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <span className="text-gray-400">Duration:</span>
                            <span className="font-semibold text-white">{config.simulation_days} days</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <span className="text-gray-400">Seeds:</span>
                            <span className="font-semibold text-white">{config.n_seed_infections}</span>
                        </div>
                        {config.custom_interventions.length > 0 && (
                            <div className="flex items-center gap-1.5">
                                <span className="text-gray-400">Interventions:</span>
                                <span className="font-semibold text-green-400">{config.custom_interventions.length}</span>
                            </div>
                        )}
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading || isRunning}
                        className={`py-3 px-8 rounded-lg font-bold text-base text-white transition-all whitespace-nowrap ${loading || isRunning
                            ? 'bg-gray-500 cursor-not-allowed'
                            : 'bg-indigo-600 hover:bg-indigo-700 shadow-lg hover:shadow-xl'
                            }`}
                    >
                        {loading ? '⏳ Starting...' : isRunning ? '⚡ Running...' : '🚀 Run Simulation'}
                    </button>
                </div>
            </form>
        </div>
    )
}
