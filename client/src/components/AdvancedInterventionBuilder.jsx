// components/AdvancedInterventionBuilder.jsx
import { useState } from 'react'

export default function AdvancedInterventionBuilder({ onInterventionsChange, initialInterventions = [] }) {
    const [interventions, setInterventions] = useState(initialInterventions)
    const [newIntervention, setNewIntervention] = useState({
        day: 30,
        type: 'mask_mandate',
        params: { efficacy: 0.5, compliance: 0.7 }
    })

    const interventionTypes = {
        mask_mandate: { label: 'Mask Mandate', icon: '😷', color: 'blue' },
        social_distancing: { label: 'Social Distancing', icon: '↔️', color: 'green' },
        vaccination: { label: 'Vaccination Campaign', icon: '💉', color: 'purple' },
        lockdown: { label: 'Lockdown', icon: '🔒', color: 'red' },
        testing: { label: 'Testing Program', icon: '🧪', color: 'yellow' },
        school_closure: { label: 'School Closure', icon: '🏫', color: 'orange' },
        border_control: { label: 'Border Control', icon: '🛂', color: 'indigo' }
    }

    const addIntervention = () => {
        const updated = [...interventions, { ...newIntervention, id: Date.now() }]
        setInterventions(updated)
        onInterventionsChange(updated)
    }

    const removeIntervention = (id) => {
        const updated = interventions.filter(i => i.id !== id)
        setInterventions(updated)
        onInterventionsChange(updated)
    }

    const updateInterventionParam = (id, key, value) => {
        const updated = interventions.map(i =>
            i.id === id
                ? { ...i, params: { ...i.params, [key]: value } }
                : i
        )
        setInterventions(updated)
        onInterventionsChange(updated)
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
                <div className="bg-gray-700 p-3 rounded-xl shadow-lg">
                    <span className="text-2xl">🛡️</span>
                </div>
                <h3 className="text-2xl font-bold text-white">
                    Advanced Intervention Builder
                </h3>
            </div>

            {/* Add New Intervention */}
            <div className="bg-gray-700 p-6 rounded-2xl border-2 border-gray-600 shadow-xl mb-6">
                <div className="flex items-center gap-2 mb-6">
                    <span className="text-2xl">➕</span>
                    <h4 className="text-xl font-bold text-white">Add Intervention</h4>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div className="bg-gray-800 p-4 rounded-xl border border-gray-700">
                        <label className="block text-sm font-bold text-gray-200 mb-3 flex items-center justify-between">
                            <span>📅 Start Day</span>
                            <span className="text-lg text-orange-600">{newIntervention.day}</span>
                        </label>
                        <input
                            type="range"
                            min="1"
                            max="365"
                            value={newIntervention.day}
                            onChange={(e) => setNewIntervention({ ...newIntervention, day: parseInt(e.target.value) })}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-orange-600"
                        />
                    </div>

                    <div className="bg-gray-800 p-4 rounded-xl border border-gray-700">
                        <label className="block text-sm font-bold text-gray-200 mb-3">
                            🎯 Intervention Type
                        </label>
                        <select
                            value={newIntervention.type}
                            onChange={(e) => setNewIntervention({
                                ...newIntervention,
                                type: e.target.value,
                                params: getDefaultParams(e.target.value)
                            })}
                            className="w-full px-4 py-3 border-2 border-gray-700 rounded-xl focus:border-orange-500 focus:ring-4 focus:ring-orange-900 transition-all duration-200 bg-gray-700 cursor-pointer font-medium text-white"
                        >
                            {Object.entries(interventionTypes).map(([key, { label, icon }]) => (
                                <option key={key} value={key}>
                                    {icon} {label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="flex items-end">
                        <button
                            onClick={addIntervention}
                            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-all"
                        >
                            ➕ Add
                        </button>
                    </div>
                </div>

                {/* Parameter Preview for New Intervention */}
                <div className="bg-gray-800 p-3 rounded border border-gray-700">
                    <div className="text-xs text-gray-300 mb-2">Parameters for {interventionTypes[newIntervention.type].label}:</div>
                    <InterventionParams
                        type={newIntervention.type}
                        params={newIntervention.params}
                        onChange={(key, value) => setNewIntervention({
                            ...newIntervention,
                            params: { ...newIntervention.params, [key]: value }
                        })}
                        compact={true}
                    />
                </div>
            </div>

            {/* Current Interventions */}
            <div>
                <h4 className="font-semibold text-white mb-4">📅 Scheduled Interventions</h4>

                {interventions.length === 0 ? (
                    <div className="bg-gray-800 p-6 rounded-lg text-center text-gray-400">
                        No interventions scheduled. Add interventions above to see them here.
                    </div>
                ) : (
                    <div className="space-y-3">
                        {interventions
                            .sort((a, b) => a.day - b.day)
                            .map(intervention => (
                                <InterventionCard
                                    key={intervention.id}
                                    intervention={intervention}
                                    interventionTypes={interventionTypes}
                                    onRemove={() => removeIntervention(intervention.id)}
                                    onParamChange={(key, value) => updateInterventionParam(intervention.id, key, value)}
                                />
                            ))}
                    </div>
                )}
            </div>

            {/* Timeline Visualization */}
            {interventions.length > 0 && (
                <div className="mt-6 bg-gray-700 p-4 rounded-lg border border-gray-600">
                    <h4 className="font-semibold text-white mb-3">📆 Intervention Timeline</h4>
                    <div className="relative h-16 bg-gray-700 rounded">
                        {interventions.map(intervention => {
                            const position = (intervention.day / 365) * 100
                            const config = interventionTypes[intervention.type]
                            return (
                                <div
                                    key={intervention.id}
                                    className={`absolute top-1/2 transform -translate-y-1/2 w-3 h-3 bg-${config.color}-500 rounded-full border-2 border-white`}
                                    style={{ left: `${position}%` }}
                                    title={`Day ${intervention.day}: ${config.label}`}
                                />
                            )
                        })}
                    </div>
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                        <span>Day 0</span>
                        <span>Day 365</span>
                    </div>
                </div>
            )}
        </div>
    )
}

function InterventionCard({ intervention, interventionTypes, onRemove, onParamChange }) {
    const config = interventionTypes[intervention.type]
    const [expanded, setExpanded] = useState(false)

    return (
        <div className={`bg-gray-700 border-2 border-${config.color}-700 rounded-lg p-4`}>
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                    <div className="text-2xl">{config.icon}</div>
                    <div>
                        <div className="font-semibold text-white">{config.label}</div>
                        <div className="text-sm text-gray-300">Day {intervention.day}</div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setExpanded(!expanded)}
                        className="px-3 py-1 text-sm bg-gray-600 text-gray-200 rounded hover:bg-gray-500"
                    >
                        {expanded ? '▲' : '▼'}
                    </button>
                    <button
                        onClick={onRemove}
                        className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                    >
                        ✕
                    </button>
                </div>
            </div>

            {expanded && (
                <div className="mt-4 pt-4 border-t border-gray-700">
                    <InterventionParams
                        type={intervention.type}
                        params={intervention.params}
                        onChange={onParamChange}
                    />
                </div>
            )}
        </div>
    )
}

function InterventionParams({ type, params, onChange, compact = false }) {
    const renderMaskParams = () => (
        <div className={`grid ${compact ? 'grid-cols-2' : 'grid-cols-1 md:grid-cols-2'} gap-3`}>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Efficacy: {((params.efficacy || 0.5) * 100).toFixed(0)}%
                </label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={params.efficacy || 0.5}
                    onChange={(e) => onChange('efficacy', parseFloat(e.target.value))}
                    className="w-full accent-blue-500"
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Compliance: {((params.compliance || 0.7) * 100).toFixed(0)}%
                </label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={params.compliance || 0.7}
                    onChange={(e) => onChange('compliance', parseFloat(e.target.value))}
                    className="w-full accent-blue-500"
                />
            </div>
        </div>
    )

    const renderDistancingParams = () => (
        <div className={`grid ${compact ? 'grid-cols-2' : 'grid-cols-1 md:grid-cols-2'} gap-3`}>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Contact Reduction: {((params.reduction || 0.4) * 100).toFixed(0)}%
                </label>
                <input
                    type="range"
                    min="0"
                    max="0.8"
                    step="0.01"
                    value={params.reduction || 0.4}
                    onChange={(e) => onChange('reduction', parseFloat(e.target.value))}
                    className="w-full accent-green-500"
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Compliance: {((params.compliance || 0.6) * 100).toFixed(0)}%
                </label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={params.compliance || 0.6}
                    onChange={(e) => onChange('compliance', parseFloat(e.target.value))}
                    className="w-full accent-green-500"
                />
            </div>
        </div>
    )

    const renderVaccinationParams = () => (
        <div className={`grid ${compact ? 'grid-cols-3' : 'grid-cols-1 md:grid-cols-3'} gap-3`}>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Daily Rate: {((params.rate || 0.01) * 100).toFixed(2)}%
                </label>
                <input
                    type="range"
                    min="0"
                    max="0.05"
                    step="0.001"
                    value={params.rate || 0.01}
                    onChange={(e) => onChange('rate', parseFloat(e.target.value))}
                    className="w-full accent-purple-500"
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Efficacy: {((params.efficacy || 0.85) * 100).toFixed(0)}%
                </label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={params.efficacy || 0.85}
                    onChange={(e) => onChange('efficacy', parseFloat(e.target.value))}
                    className="w-full accent-purple-500"
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Priority
                </label>
                <select
                    value={params.priority || 'elderly'}
                    onChange={(e) => onChange('priority', e.target.value)}
                    className="w-full px-2 py-1 border border-gray-600 bg-gray-800 text-white rounded text-xs"
                >
                    <option value="elderly">Elderly First</option>
                    <option value="vulnerable">Vulnerable</option>
                    <option value="random">Random</option>
                    <option value="young">Young First</option>
                </select>
            </div>
        </div>
    )

    const renderLockdownParams = () => (
        <div className={`grid ${compact ? 'grid-cols-2' : 'grid-cols-1 md:grid-cols-2'} gap-3`}>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Strictness: {((params.strictness || 0.7) * 100).toFixed(0)}%
                </label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={params.strictness || 0.7}
                    onChange={(e) => onChange('strictness', parseFloat(e.target.value))}
                    className="w-full accent-red-500"
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Duration: {params.duration || 14} days
                </label>
                <input
                    type="range"
                    min="7"
                    max="90"
                    step="1"
                    value={params.duration || 14}
                    onChange={(e) => onChange('duration', parseInt(e.target.value))}
                    className="w-full accent-red-500"
                />
            </div>
        </div>
    )

    const renderTestingParams = () => (
        <div className={`grid ${compact ? 'grid-cols-3' : 'grid-cols-1 md:grid-cols-3'} gap-3`}>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Daily Rate: {((params.rate || 0.05) * 100).toFixed(1)}%
                </label>
                <input
                    type="range"
                    min="0"
                    max="0.2"
                    step="0.001"
                    value={params.rate || 0.05}
                    onChange={(e) => onChange('rate', parseFloat(e.target.value))}
                    className="w-full accent-yellow-500"
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Accuracy: {((params.accuracy || 0.95) * 100).toFixed(0)}%
                </label>
                <input
                    type="range"
                    min="0.5"
                    max="1"
                    step="0.01"
                    value={params.accuracy || 0.95}
                    onChange={(e) => onChange('accuracy', parseFloat(e.target.value))}
                    className="w-full accent-yellow-500"
                />
            </div>
            <div>
                <label className="block text-xs font-medium text-gray-300 mb-1">
                    Result Delay: {params.delay || 1} days
                </label>
                <input
                    type="range"
                    min="0"
                    max="5"
                    step="1"
                    value={params.delay || 1}
                    onChange={(e) => onChange('delay', parseInt(e.target.value))}
                    className="w-full accent-yellow-500"
                />
            </div>
        </div>
    )

    switch (type) {
        case 'mask_mandate':
            return renderMaskParams()
        case 'social_distancing':
            return renderDistancingParams()
        case 'vaccination':
            return renderVaccinationParams()
        case 'lockdown':
            return renderLockdownParams()
        case 'testing':
            return renderTestingParams()
        case 'school_closure':
            return renderDistancingParams() // Similar params
        case 'border_control':
            return renderDistancingParams() // Similar params
        default:
            return <div className="text-sm text-gray-400">No parameters available</div>
    }
}

function getDefaultParams(type) {
    const defaults = {
        mask_mandate: { efficacy: 0.5, compliance: 0.7 },
        social_distancing: { reduction: 0.4, compliance: 0.6 },
        vaccination: { rate: 0.01, efficacy: 0.85, priority: 'elderly' },
        lockdown: { strictness: 0.7, duration: 14 },
        testing: { rate: 0.05, accuracy: 0.95, delay: 1 },
        school_closure: { reduction: 0.6, compliance: 0.9 },
        border_control: { reduction: 0.8, compliance: 0.95 }
    }
    return defaults[type] || {}
}
