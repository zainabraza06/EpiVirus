// components/CustomDiseaseBuilder.jsx
import { useState } from 'react'

export default function CustomDiseaseBuilder({ onParamsChange, initialParams = {} }) {
    const [params, setParams] = useState({
        base_transmission_rate: 0.05,
        incubation_period: 5.0,
        infectious_period: 7.0,
        asymptomatic_rate: 0.3,
        hospitalization_rate: 0.05,
        icu_rate: 0.01,
        mortality_rate: 0.01,
        r0: 2.5,
        ...initialParams
    })

    const handleChange = (key, value) => {
        const newParams = { ...params, [key]: value }
        setParams(newParams)
        onParamsChange(newParams)
    }

    return (
        <div className="bg-gray-700 rounded-xl border border-gray-600 p-6 space-y-6">
            <div className="flex items-center gap-3 mb-4">
                <div className="bg-gray-800 p-2 rounded-lg">
                    <span className="text-2xl">🦠</span>
                </div>
                <h3 className="text-xl font-bold text-white">
                    Custom Disease Parameters
                </h3>
            </div>

            {/* Main Grid - 3 Columns */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Column 1: Transmission Parameters */}
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-600 space-y-4">
                    <h4 className="font-semibold text-red-300 border-b border-red-900 pb-2 flex items-center gap-2">
                        <span>🦠</span>
                        <span>Transmission</span>
                    </h4>

                    <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1 flex items-center justify-between">
                            <span>Transmission Rate (β)</span>
                            <span className="text-sm text-red-400 font-semibold">{params.base_transmission_rate.toFixed(3)}</span>
                        </label>
                        <input
                            type="range"
                            min="0.01"
                            max="0.2"
                            step="0.001"
                            value={params.base_transmission_rate}
                            onChange={(e) => handleChange('base_transmission_rate', parseFloat(e.target.value))}
                            className="w-full accent-red-500"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                            Transmission probability per contact
                        </p>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1 flex items-center justify-between">
                            <span>R₀</span>
                            <span className="text-sm text-red-400 font-semibold">{params.r0.toFixed(2)}</span>
                        </label>
                        <input
                            type="range"
                            min="0.5"
                            max="10"
                            step="0.1"
                            value={params.r0}
                            onChange={(e) => handleChange('r0', parseFloat(e.target.value))}
                            className="w-full accent-red-500"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                            Secondary infections per case
                        </p>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1 flex items-center justify-between">
                            <span>Asymptomatic Rate</span>
                            <span className="text-sm text-red-400 font-semibold">{(params.asymptomatic_rate * 100).toFixed(0)}%</span>
                        </label>
                        <input
                            type="range"
                            min="0"
                            max="0.8"
                            step="0.01"
                            value={params.asymptomatic_rate}
                            onChange={(e) => handleChange('asymptomatic_rate', parseFloat(e.target.value))}
                            className="w-full accent-red-500"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                            Infections without symptoms
                        </p>
                    </div>
                </div>

                {/* Column 2: Disease Progression */}
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-600 space-y-4">
                    <h4 className="font-semibold text-yellow-300 border-b border-yellow-900 pb-2 flex items-center gap-2">
                        <span>⏱️</span>
                        <span>Disease Timeline</span>
                    </h4>

                    <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1 flex items-center justify-between">
                            <span>Incubation Period</span>
                            <span className="text-sm text-yellow-400 font-semibold">{params.incubation_period.toFixed(1)} days</span>
                        </label>
                        <input
                            type="range"
                            min="1"
                            max="14"
                            step="0.5"
                            value={params.incubation_period}
                            onChange={(e) => handleChange('incubation_period', parseFloat(e.target.value))}
                            className="w-full accent-yellow-500"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                            Time to symptom onset
                        </p>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1 flex items-center justify-between">
                            <span>Infectious Period</span>
                            <span className="text-sm text-yellow-400 font-semibold">{params.infectious_period.toFixed(1)} days</span>
                        </label>
                        <input
                            type="range"
                            min="1"
                            max="21"
                            step="0.5"
                            value={params.infectious_period}
                            onChange={(e) => handleChange('infectious_period', parseFloat(e.target.value))}
                            className="w-full accent-yellow-500"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                            Duration of infectiousness
                        </p>
                    </div>

                    <div className="bg-gray-900 p-3 rounded border border-gray-700 mt-4">
                        <p className="text-xs text-gray-300 font-semibold mb-2">Timeline Summary:</p>
                        <div className="text-xs text-gray-400 space-y-1">
                            <div>• Total disease duration: {(params.incubation_period + params.infectious_period).toFixed(1)} days</div>
                            <div>• Generation time: ~{((params.incubation_period + params.infectious_period) / 2).toFixed(1)} days</div>
                        </div>
                    </div>
                </div>

                {/* Column 3: Severity Parameters */}
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-600 space-y-4">
                    <h4 className="font-semibold text-orange-300 border-b border-orange-900 pb-2 flex items-center gap-2">
                        <span>🏥</span>
                        <span>Severity</span>
                    </h4>

                    <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1 flex items-center justify-between">
                            <span>Hospitalization Rate</span>
                            <span className="text-sm text-orange-400 font-semibold">{(params.hospitalization_rate * 100).toFixed(1)}%</span>
                        </label>
                        <input
                            type="range"
                            min="0"
                            max="0.3"
                            step="0.001"
                            value={params.hospitalization_rate}
                            onChange={(e) => handleChange('hospitalization_rate', parseFloat(e.target.value))}
                            className="w-full accent-orange-500"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                            Require hospitalization
                        </p>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1 flex items-center justify-between">
                            <span>ICU Rate</span>
                            <span className="text-sm text-orange-400 font-semibold">{(params.icu_rate * 100).toFixed(2)}%</span>
                        </label>
                        <input
                            type="range"
                            min="0"
                            max="0.1"
                            step="0.001"
                            value={params.icu_rate}
                            onChange={(e) => handleChange('icu_rate', parseFloat(e.target.value))}
                            className="w-full accent-orange-500"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                            Require intensive care
                        </p>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1 flex items-center justify-between">
                            <span>Mortality Rate (CFR)</span>
                            <span className="text-sm text-orange-400 font-semibold">{(params.mortality_rate * 100).toFixed(2)}%</span>
                        </label>
                        <input
                            type="range"
                            min="0"
                            max="0.1"
                            step="0.001"
                            value={params.mortality_rate}
                            onChange={(e) => handleChange('mortality_rate', parseFloat(e.target.value))}
                            className="w-full accent-orange-500"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                            Case fatality rate
                        </p>
                    </div>
                </div>
            </div>

            {/* Age Stratification Info - Full Width */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-600">
                <h4 className="font-semibold text-purple-300 border-b border-purple-900 pb-2 mb-3 flex items-center gap-2">
                    <span>👥</span>
                    <span>Age Stratification</span>
                </h4>
                <p className="text-xs text-gray-300 mb-3">
                    Age-specific parameters will be automatically calculated based on these baseline values.
                </p>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 text-xs text-gray-300">
                    <div className="bg-gray-900 p-2 rounded">
                        <strong className="text-purple-300">0-17:</strong> Lower severity, moderate transmission
                    </div>
                    <div className="bg-gray-900 p-2 rounded">
                        <strong className="text-purple-300">18-49:</strong> Baseline severity, high transmission
                    </div>
                    <div className="bg-gray-900 p-2 rounded">
                        <strong className="text-purple-300">50-64:</strong> Increased severity, baseline transmission
                    </div>
                    <div className="bg-gray-900 p-2 rounded">
                        <strong className="text-purple-300">65+:</strong> High severity, reduced transmission
                    </div>
                </div>
            </div>

            {/* Summary - Full Width */}
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                <h4 className="font-semibold text-white mb-3 text-sm">📋 Disease Profile Summary</h4>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div className="flex justify-between">
                        <span className="text-gray-300">R₀:</span>
                        <span className="font-semibold text-red-400">{params.r0.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-300">Incubation:</span>
                        <span className="font-semibold text-yellow-400">{params.incubation_period.toFixed(1)}d</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-300">Infectious:</span>
                        <span className="font-semibold text-yellow-400">{params.infectious_period.toFixed(1)}d</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-300">CFR:</span>
                        <span className="font-semibold text-orange-400">{(params.mortality_rate * 100).toFixed(2)}%</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
