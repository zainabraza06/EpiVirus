// components/results/SimulationResults.jsx
//
// Headline numbers for the Analysis tab. Deliberately a short strip: the full
// metric grid and the daily table live in the Results tab, and duplicating them
// here is what made three tabs show the same figures.
import { STATE_COLORS } from '../charts/chartTokens'

export default function SimulationResults({ results }) {
    const summary = results?.summary ?? {}
    const population = summary.initial_population || 1

    const tiles = [
        {
            label: 'Attack rate',
            value: `${((summary.attack_rate ?? 0) * 100).toFixed(1)}%`,
            detail: `${(summary.total_infected ?? 0).toLocaleString()} of ${population.toLocaleString()} infected`,
            accent: STATE_COLORS.I,
        },
        {
            label: 'Peak infections',
            value: (summary.peak_infections ?? 0).toLocaleString(),
            detail: `on day ${summary.peak_day ?? 0}`,
            accent: STATE_COLORS.E,
        },
        {
            label: 'Deaths',
            value: (summary.total_deaths ?? 0).toLocaleString(),
            detail: `${((summary.case_fatality_rate ?? 0) * 100).toFixed(2)}% of cases`,
            accent: STATE_COLORS.D,
        },
        {
            label: 'Recovered',
            value: (summary.total_recovered ?? 0).toLocaleString(),
            detail: `${(summary.total_hospitalized ?? 0).toLocaleString()} were hospitalised`,
            accent: STATE_COLORS.R,
        },
        {
            label: 'Final R effective',
            value: (summary.final_r_effective ?? 0).toFixed(2),
            detail: (summary.final_r_effective ?? 0) > 1 ? 'still growing' : 'under control',
            accent: STATE_COLORS.V,
        },
    ]

    return (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            {tiles.map((tile) => (
                <div
                    key={tile.label}
                    className="bg-gray-800 rounded-xl border border-gray-700 p-5 shadow-lg border-l-4"
                    style={{ borderLeftColor: tile.accent }}
                >
                    <div className="text-xs text-gray-400 uppercase tracking-wide">{tile.label}</div>
                    <div className="text-3xl font-bold text-white mt-1 tabular-nums">{tile.value}</div>
                    <div className="text-xs text-gray-400 mt-1">{tile.detail}</div>
                </div>
            ))}
        </div>
    )
}
