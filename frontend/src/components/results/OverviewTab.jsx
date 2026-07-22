// components/results/OverviewTab.jsx
import { STATE_COLORS, STATE_LABELS } from '../charts/chartTokens'

const FEATURES = [
    {
        icon: '🌐',
        title: 'Contact networks',
        body: 'Five topologies, from uniform random graphs to a multilayer network of households, workplaces and schools.',
    },
    {
        icon: '🦠',
        title: 'Disease model',
        body: 'SEIRD compartments with five severity levels and nine age bands, or build a variant from scratch.',
    },
    {
        icon: '🛡️',
        title: 'Interventions',
        body: 'Masks, distancing, testing, lockdowns and vaccination campaigns, on a schedule you control.',
    },
]

const STEPS = [
    'Open the Simulation tab and set the population, network and disease.',
    'Pick an intervention scenario, or schedule your own.',
    'Run the simulation and watch the progress bar.',
    'Read the charts in Analysis, then replay the outbreak in Network.',
    'Export the raw numbers from Results.',
]

export default function OverviewTab({
    hasSimulation,
    results,
    isRunning,
    onRunExample,
    onNewSimulation,
    onGoToSimulation,
}) {
    const summary = results?.summary

    return (
        <div className="space-y-8">
            <section className="text-center py-10">
                <h1 className="text-5xl font-bold text-white mb-3">EpiVirus</h1>
                <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                    Watch a disease move through a population one contact at a time, and see what
                    changes when you intervene.
                </p>
                <div className="flex flex-wrap gap-3 justify-center mt-8">
                    <button
                        type="button"
                        onClick={onRunExample}
                        disabled={isRunning}
                        className="px-6 py-3 rounded-lg font-semibold text-white bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 disabled:text-gray-400 transition-colors"
                    >
                        {isRunning ? 'Simulation running…' : 'Run an example simulation'}
                    </button>
                    <button
                        type="button"
                        onClick={hasSimulation ? onNewSimulation : onGoToSimulation}
                        className="px-6 py-3 rounded-lg font-semibold text-gray-200 bg-gray-800 border border-gray-700 hover:bg-gray-700 transition-colors"
                    >
                        {hasSimulation ? 'Start over' : 'Configure your own'}
                    </button>
                </div>
            </section>

            {summary && (
                <section className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg">
                    <h2 className="text-lg font-semibold text-white mb-4">Latest simulation</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            ['Population', summary.initial_population],
                            ['Infected', summary.total_infected],
                            ['Deaths', summary.total_deaths],
                            ['Peak day', summary.peak_day],
                        ].map(([label, value]) => (
                            <div key={label} className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                                <div className="text-xs text-gray-400 uppercase tracking-wide">{label}</div>
                                <div className="text-2xl font-bold text-white mt-1 tabular-nums">
                                    {(value ?? 0).toLocaleString()}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {FEATURES.map((feature) => (
                    <div
                        key={feature.title}
                        className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg"
                    >
                        <div className="text-3xl mb-3" aria-hidden="true">{feature.icon}</div>
                        <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                        <p className="text-sm text-gray-400 leading-relaxed">{feature.body}</p>
                    </div>
                ))}
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg">
                    <h2 className="text-lg font-semibold text-white mb-4">How it works</h2>
                    <ol className="space-y-3">
                        {STEPS.map((step, index) => (
                            <li key={step} className="flex gap-3 text-gray-300">
                                <span className="shrink-0 w-7 h-7 rounded-full bg-gray-700 text-white text-sm font-bold flex items-center justify-center">
                                    {index + 1}
                                </span>
                                <span className="pt-0.5">{step}</span>
                            </li>
                        ))}
                    </ol>
                </div>

                <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg">
                    <h2 className="text-lg font-semibold text-white mb-4">Compartments</h2>
                    <ul className="space-y-3">
                        {Object.entries(STATE_LABELS).map(([key, label]) => (
                            <li key={key} className="flex items-center gap-3">
                                <span
                                    className="w-4 h-4 rounded-full shrink-0"
                                    style={{ backgroundColor: STATE_COLORS[key] }}
                                />
                                <span className="text-sm text-gray-300 flex-1">{label}</span>
                                <span className="text-xs text-gray-500 font-mono">{key}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </section>
        </div>
    )
}
