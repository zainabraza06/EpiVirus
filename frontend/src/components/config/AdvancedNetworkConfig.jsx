// components/config/AdvancedNetworkConfig.jsx
//
// Only controls the backend actually reads are exposed here. The previous
// version offered household-size and per-layer sliders that no API field
// accepted, so moving them changed nothing about the generated network.

const CONTROLS = {
    erdos_renyi: [
        {
            key: 'erdos_p',
            label: 'Connection probability',
            min: 0.001,
            max: 0.1,
            step: 0.001,
            decimals: 3,
            hint: 'Chance that any two people are connected.',
        },
    ],
    watts_strogatz: [
        {
            key: 'watts_k',
            label: 'Neighbours per person',
            min: 2,
            max: 20,
            step: 2,
            integer: true,
            hint: 'Ring-lattice degree before rewiring. Must be even.',
        },
        {
            key: 'watts_p',
            label: 'Rewiring probability',
            min: 0,
            max: 1,
            step: 0.01,
            decimals: 2,
            hint: 'Higher values trade clustering for short paths.',
        },
    ],
    barabasi_albert: [
        {
            key: 'barabasi_m',
            label: 'Edges per new person',
            min: 1,
            max: 10,
            step: 1,
            integer: true,
            hint: 'Preferential attachment strength; higher values grow bigger hubs.',
        },
    ],
    stochastic_block: [
        {
            key: 'n_blocks',
            label: 'Communities',
            min: 2,
            max: 20,
            step: 1,
            integer: true,
            hint: 'The population is split evenly across this many communities.',
        },
        {
            key: 'block_intra',
            label: 'Within-community probability',
            min: 0.01,
            max: 0.5,
            step: 0.01,
            decimals: 2,
            hint: 'Connection chance between two people in the same community.',
        },
        {
            key: 'block_inter',
            label: 'Between-community probability',
            min: 0.001,
            max: 0.1,
            step: 0.001,
            decimals: 3,
            hint: 'Connection chance across communities. Low values isolate outbreaks.',
        },
    ],
    hybrid: [
        {
            key: 'workplace_p',
            label: 'Workplace contact probability',
            min: 0.1,
            max: 1,
            step: 0.05,
            decimals: 2,
            hint: 'How densely colleagues in the same workplace are connected.',
        },
        {
            key: 'school_p',
            label: 'School contact probability',
            min: 0.1,
            max: 1,
            step: 0.05,
            decimals: 2,
            hint: 'How densely pupils in the same school are connected.',
        },
        {
            key: 'community_p',
            label: 'Community mixing',
            min: 0,
            max: 2,
            step: 0.05,
            decimals: 2,
            hint: 'Long-distance contacts added per person, on top of the layers.',
        },
    ],
}

const DEFAULTS = {
    erdos_p: 0.01,
    watts_k: 8,
    watts_p: 0.3,
    barabasi_m: 3,
    n_blocks: 4,
    block_intra: 0.15,
    block_inter: 0.01,
    workplace_p: 0.6,
    school_p: 0.8,
    community_p: 0.4,
}

export default function AdvancedNetworkConfig({ networkType, params = {}, onParamsChange }) {
    const controls = CONTROLS[networkType] ?? []

    return (
        <div className="bg-gray-900/60 rounded-xl border border-gray-700 p-5">
            <h3 className="font-semibold text-white mb-1">Advanced network parameters</h3>
            <p className="text-sm text-gray-400 mb-4">
                {controls.length
                    ? `Tuning for the ${networkType.replace(/_/g, ' ')} topology.`
                    : 'This topology has no additional parameters.'}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {controls.map((control) => {
                    const value = params[control.key] ?? DEFAULTS[control.key]
                    const display = control.integer
                        ? value
                        : Number(value).toFixed(control.decimals ?? 2)

                    return (
                        <label key={control.key} className="block bg-gray-800 rounded-lg border border-gray-700 p-4">
                            <span className="flex justify-between text-xs font-medium text-gray-400 mb-2">
                                <span>{control.label}</span>
                                <span className="text-gray-100 font-semibold">{display}</span>
                            </span>
                            <input
                                type="range"
                                min={control.min}
                                max={control.max}
                                step={control.step}
                                value={value}
                                onChange={(event) => {
                                    const parsed = control.integer
                                        ? parseInt(event.target.value, 10)
                                        : parseFloat(event.target.value)
                                    if (!Number.isNaN(parsed)) {
                                        onParamsChange({ [control.key]: parsed })
                                    }
                                }}
                                className="w-full accent-indigo-500"
                            />
                            <span className="block text-xs text-gray-500 mt-2">{control.hint}</span>
                        </label>
                    )
                })}
            </div>
        </div>
    )
}
