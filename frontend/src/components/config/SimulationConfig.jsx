// components/config/SimulationConfig.jsx
import { useMemo, useState } from 'react'
import AdvancedNetworkConfig from './AdvancedNetworkConfig'
import CustomDiseaseBuilder from './CustomDiseaseBuilder'
import AdvancedInterventionBuilder from './AdvancedInterventionBuilder'

const DEFAULT_DISEASES = [
    { id: 'wildtype', name: 'COVID-19 (Wildtype)', r0: 2.5, mortality_rate: 0.02 },
    { id: 'alpha', name: 'COVID-19 (Alpha)', r0: 4.0, mortality_rate: 0.025 },
    { id: 'delta', name: 'COVID-19 (Delta)', r0: 5.0, mortality_rate: 0.03 },
    { id: 'omicron', name: 'COVID-19 (Omicron)', r0: 9.5, mortality_rate: 0.01 },
]

const DEFAULT_NETWORKS = [
    { id: 'hybrid', name: 'Hybrid Multilayer', description: 'Households, workplaces and schools' },
    { id: 'erdos_renyi', name: 'Erdős-Rényi', description: 'Uniform random connections' },
    { id: 'watts_strogatz', name: 'Watts-Strogatz', description: 'Small-world clustering' },
    { id: 'barabasi_albert', name: 'Barabási-Albert', description: 'Scale-free, with hubs' },
    { id: 'stochastic_block', name: 'Stochastic Block', description: 'Distinct communities' },
]

const SCENARIOS = [
    { id: 'no_intervention', name: 'No intervention', description: 'Natural spread, no countermeasures' },
    { id: 'rapid_response', name: 'Rapid response', description: 'Masks day 7, testing day 14, distancing day 21' },
    { id: 'delayed_response', name: 'Delayed response', description: 'Masks day 30, lockdown day 75' },
    { id: 'herd_immunity', name: 'Herd immunity', description: 'Mass vaccination from day 0' },
    { id: 'full_lockdown', name: 'Full lockdown', description: 'Strict lockdown day 14, reopening day 45' },
]

const SEED_METHODS = [
    { id: 'random', name: 'Random' },
    { id: 'hubs', name: 'Network hubs' },
    { id: 'mobile', name: 'High mobility' },
    { id: 'geographic', name: 'Geographic cluster' },
    { id: 'age_targeted', name: 'Age targeted' },
]

// The disease builder speaks its own vocabulary; this maps it onto the API's
// custom_params shape. Without the translation the whole panel was dropped on
// the floor by request validation.
function toCustomDiseaseParams(builderParams) {
    if (!builderParams) return null

    const asymptomatic = builderParams.asymptomatic_rate ?? 0.3
    // The remaining probability mass is split across the symptomatic tiers,
    // weighted by the hospitalisation and ICU rates the user chose.
    const critical = builderParams.icu_rate ?? 0.01
    const severe = Math.max(0, (builderParams.hospitalization_rate ?? 0.05) - critical)
    const mild = Math.max(0, 1 - asymptomatic - severe - critical)

    return {
        name: 'Custom disease',
        r0: builderParams.r0,
        mortality_rate: builderParams.mortality_rate,
        hospitalization_rate: builderParams.hospitalization_rate,
        incubation_mean: builderParams.incubation_period,
        infectious_mean: builderParams.infectious_period,
        p_asymptomatic: asymptomatic,
        p_mild: mild,
        p_severe: severe,
        p_critical: critical,
    }
}

export default function SimulationConfig({ diseases, networks, onStartSimulation, loading, running }) {
    const resolvedDiseases = diseases?.length ? diseases : DEFAULT_DISEASES
    const resolvedNetworks = networks?.length ? networks : DEFAULT_NETWORKS

    const [network, setNetwork] = useState({
        population: 1000,
        network_type: 'hybrid',
        erdos_p: 0.01,
        watts_k: 8,
        watts_p: 0.3,
        barabasi_m: 3,
        n_blocks: 4,
        block_intra: 0.15,
        block_inter: 0.01,
    })
    const [variant, setVariant] = useState('omicron')
    const [customDisease, setCustomDisease] = useState(null)
    const [useCustomDisease, setUseCustomDisease] = useState(false)
    const [customInterventions, setCustomInterventions] = useState([])
    const [settings, setSettings] = useState({
        n_seed_infections: 10,
        seed_method: 'random',
        simulation_days: 120,
        intervention_scenario: 'no_intervention',
        vaccination_rate: 0.0,
        compliance_rate: 0.8,
    })
    const [openPanel, setOpenPanel] = useState(null)

    const selectedDisease = useMemo(
        () => resolvedDiseases.find((d) => d.id === variant),
        [resolvedDiseases, variant]
    )

    const update = (setter) => (field, value) =>
        setter((previous) => ({ ...previous, [field]: value }))

    const updateNetwork = update(setNetwork)
    const updateSettings = update(setSettings)

    const handleSubmit = (event) => {
        event.preventDefault()
        onStartSimulation({
            network,
            disease: {
                variant,
                custom_params: useCustomDisease ? toCustomDiseaseParams(customDisease) : null,
            },
            ...settings,
            // Seeds cannot exceed the population
            n_seed_infections: Math.min(settings.n_seed_infections, network.population),
            custom_interventions: customInterventions,
        })
    }

    const disabled = loading || running
    const panels = [
        ['network', '🌐 Advanced network'],
        ['disease', '🦠 Custom disease'],
        ['intervention', '🛡️ Custom interventions'],
    ]

    return (
        <form onSubmit={handleSubmit} className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg space-y-6">
            <div>
                <h2 className="text-xl font-bold text-white">Simulation setup</h2>
                <p className="text-sm text-gray-400">Every setting here is sent to the model.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <Panel title="Network" accent="border-indigo-500">
                    <Field label="Population">
                        <input
                            type="number"
                            value={network.population}
                            onChange={(e) => {
                                const value = parseInt(e.target.value, 10)
                                if (!Number.isNaN(value)) updateNetwork('population', value)
                            }}
                            min="50"
                            max="10000"
                            step="50"
                            className={inputClass}
                        />
                        <Hint>50–10,000 people. Large runs take noticeably longer.</Hint>
                    </Field>
                    <Field label="Topology">
                        <select
                            value={network.network_type}
                            onChange={(e) => updateNetwork('network_type', e.target.value)}
                            className={inputClass}
                        >
                            {resolvedNetworks.map((net) => (
                                <option key={net.id} value={net.id}>{net.name}</option>
                            ))}
                        </select>
                        <Hint>{resolvedNetworks.find((n) => n.id === network.network_type)?.description}</Hint>
                    </Field>
                </Panel>

                <Panel title="Disease" accent="border-rose-500">
                    <Field label="Variant">
                        <select
                            value={variant}
                            onChange={(e) => setVariant(e.target.value)}
                            disabled={useCustomDisease}
                            className={inputClass}
                        >
                            {resolvedDiseases.map((disease) => (
                                <option key={disease.id} value={disease.id}>{disease.name}</option>
                            ))}
                        </select>
                    </Field>
                    {selectedDisease && !useCustomDisease && (
                        <div className="bg-gray-900 rounded-lg p-3 text-xs text-gray-300 space-y-1 border border-gray-700">
                            <div className="flex justify-between">
                                <span>R₀</span>
                                <span className="font-semibold text-rose-400">{selectedDisease.r0}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Case fatality rate</span>
                                <span className="font-semibold text-rose-400">
                                    {(selectedDisease.mortality_rate * 100).toFixed(1)}%
                                </span>
                            </div>
                        </div>
                    )}
                    <label className="flex items-center gap-2 text-sm text-gray-300">
                        <input
                            type="checkbox"
                            checked={useCustomDisease}
                            onChange={(e) => {
                                setUseCustomDisease(e.target.checked)
                                if (e.target.checked) setOpenPanel('disease')
                            }}
                            className="accent-rose-500"
                        />
                        Use custom disease parameters
                    </label>
                </Panel>

                <Panel title="Seeding" accent="border-amber-500">
                    <Slider
                        label="Initial infections"
                        value={settings.n_seed_infections}
                        display={settings.n_seed_infections}
                        min={1}
                        max={Math.min(200, network.population)}
                        step={1}
                        accent="accent-amber-500"
                        onChange={(v) => updateSettings('n_seed_infections', v)}
                    />
                    <Field label="Seeding method">
                        <select
                            value={settings.seed_method}
                            onChange={(e) => updateSettings('seed_method', e.target.value)}
                            className={inputClass}
                        >
                            {SEED_METHODS.map((method) => (
                                <option key={method.id} value={method.id}>{method.name}</option>
                            ))}
                        </select>
                    </Field>
                </Panel>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <Panel title="Duration" accent="border-purple-500">
                    <Slider
                        label="Days to simulate"
                        value={settings.simulation_days}
                        display={`${settings.simulation_days} days`}
                        min={30}
                        max={365}
                        step={5}
                        accent="accent-purple-500"
                        onChange={(v) => updateSettings('simulation_days', v)}
                    />
                </Panel>

                <Panel title="Interventions" accent="border-emerald-500">
                    <Field label="Scenario">
                        <select
                            value={settings.intervention_scenario}
                            onChange={(e) => updateSettings('intervention_scenario', e.target.value)}
                            className={inputClass}
                        >
                            {SCENARIOS.map((scenario) => (
                                <option key={scenario.id} value={scenario.id}>{scenario.name}</option>
                            ))}
                        </select>
                        <Hint>
                            {SCENARIOS.find((s) => s.id === settings.intervention_scenario)?.description}
                        </Hint>
                    </Field>
                    {settings.intervention_scenario !== 'no_intervention' && (
                        <>
                            <Slider
                                label="Vaccination rate"
                                value={settings.vaccination_rate}
                                display={`${(settings.vaccination_rate * 100).toFixed(1)}% of susceptibles per day`}
                                min={0}
                                max={0.05}
                                step={0.001}
                                accent="accent-emerald-500"
                                float
                                onChange={(v) => updateSettings('vaccination_rate', v)}
                            />
                            <Slider
                                label="Compliance"
                                value={settings.compliance_rate}
                                display={`${(settings.compliance_rate * 100).toFixed(0)}% of people comply`}
                                min={0}
                                max={1}
                                step={0.05}
                                accent="accent-emerald-500"
                                float
                                onChange={(v) => updateSettings('compliance_rate', v)}
                            />
                        </>
                    )}
                </Panel>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
                {panels.map(([id, label]) => (
                    <button
                        key={id}
                        type="button"
                        onClick={() => setOpenPanel(openPanel === id ? null : id)}
                        className="flex items-center justify-between px-4 py-3 rounded-lg bg-gray-700 hover:bg-gray-600 border border-gray-600 text-sm font-semibold text-gray-200 transition-colors"
                    >
                        <span>{label}</span>
                        <span aria-hidden="true">{openPanel === id ? '▲' : '▼'}</span>
                    </button>
                ))}
            </div>

            {openPanel === 'network' && (
                <AdvancedNetworkConfig
                    networkType={network.network_type}
                    params={network}
                    onParamsChange={(params) => setNetwork((prev) => ({ ...prev, ...params }))}
                />
            )}

            {openPanel === 'disease' && (
                <div className="space-y-3">
                    {!useCustomDisease && (
                        <p className="text-sm text-amber-300 bg-amber-950/40 border border-amber-800 rounded-lg px-4 py-2">
                            Tick “Use custom disease parameters” above for these values to take effect.
                        </p>
                    )}
                    <CustomDiseaseBuilder
                        onParamsChange={setCustomDisease}
                        initialParams={customDisease ?? {}}
                    />
                </div>
            )}

            {openPanel === 'intervention' && (
                <AdvancedInterventionBuilder
                    onInterventionsChange={setCustomInterventions}
                    initialInterventions={customInterventions}
                />
            )}

            <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-gray-700">
                <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-gray-400">
                    <span>{network.population.toLocaleString()} people</span>
                    <span>{network.network_type.replace(/_/g, ' ')}</span>
                    <span>{useCustomDisease ? 'custom disease' : variant}</span>
                    <span>{settings.simulation_days} days</span>
                    <span>{settings.intervention_scenario.replace(/_/g, ' ')}</span>
                    {customInterventions.length > 0 && (
                        <span className="text-emerald-400">
                            +{customInterventions.length} custom intervention
                            {customInterventions.length > 1 ? 's' : ''}
                        </span>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={disabled}
                    className={`px-8 py-3 rounded-lg font-bold text-white transition-colors ${
                        disabled ? 'bg-gray-600 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500'
                    }`}
                >
                    {loading ? 'Starting…' : running ? 'Running…' : 'Run simulation'}
                </button>
            </div>
        </form>
    )
}

const inputClass =
    'w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-600 text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-shadow disabled:opacity-50'

function Panel({ title, accent, children }) {
    return (
        <div className={`bg-gray-900/60 rounded-xl p-4 border border-gray-700 border-t-2 ${accent} space-y-3`}>
            <h3 className="font-semibold text-white">{title}</h3>
            {children}
        </div>
    )
}

function Field({ label, children }) {
    return (
        <label className="block">
            <span className="block text-xs font-medium text-gray-400 mb-1">{label}</span>
            {children}
        </label>
    )
}

function Hint({ children }) {
    return <p className="text-xs text-gray-500 mt-1">{children}</p>
}

function Slider({ label, value, display, min, max, step, accent, onChange, float = false }) {
    return (
        <label className="block">
            <span className="flex justify-between text-xs font-medium text-gray-400 mb-1">
                <span>{label}</span>
                <span className="text-gray-200 font-semibold">{display}</span>
            </span>
            <input
                type="range"
                value={value}
                min={min}
                max={max}
                step={step}
                onChange={(e) => {
                    const parsed = float ? parseFloat(e.target.value) : parseInt(e.target.value, 10)
                    if (!Number.isNaN(parsed)) onChange(parsed)
                }}
                className={`w-full ${accent}`}
            />
        </label>
    )
}
