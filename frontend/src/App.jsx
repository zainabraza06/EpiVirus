// src/App.jsx - EpiVirus frontend shell
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { apiUrl } from './api'

import LoadingSpinner from './components/ui/LoadingSpinner'
import SimulationConfig from './components/config/SimulationConfig'
import SimulationResults from './components/results/SimulationResults'
import NetworkInfo from './components/results/NetworkInfo'
import OverviewTab from './components/results/OverviewTab'
import NetworkView from './components/visualization/NetworkView'
import {
  AgeDistributionChart,
  CumulativeOutcomesChart,
  DailyDeathsChart,
  DegreeDistributionChart,
  EpidemicCurveChart,
  HealthcareBurdenChart,
  MobilityDistributionChart,
  PopulationCompositionChart,
  REffectiveChart,
  SeirdDynamicsChart,
  SocialClusteringChart,
} from './components/charts/EpidemicCharts'

const TABS = [
  { id: 'overview', icon: '🏠', label: 'Overview', needsResults: false },
  { id: 'simulation', icon: '⚙️', label: 'Simulation', needsResults: false },
  { id: 'analysis', icon: '📊', label: 'Analysis', needsResults: true },
  { id: 'network', icon: '🌐', label: 'Network', needsResults: true },
  { id: 'results', icon: '📈', label: 'Results', needsResults: true },
]

const POLL_INTERVAL_MS = 1500

function App() {
  const [currentSimulation, setCurrentSimulation] = useState(null)
  const [simulationStatus, setSimulationStatus] = useState(null)
  const [simulationResults, setSimulationResults] = useState(null)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState(null)
  const [availableDiseases, setAvailableDiseases] = useState([])
  const [availableNetworks, setAvailableNetworks] = useState([])
  const [activeTab, setActiveTab] = useState('overview')

  // Guards against fetching the same result set twice when the status object
  // is replaced by an identical poll response.
  const fetchedResultsFor = useRef(null)

  useEffect(() => {
    const load = async (path, setter, key) => {
      try {
        const response = await fetch(apiUrl(path))
        if (!response.ok) return
        const data = await response.json()
        setter(data[key] ?? [])
      } catch {
        // The config form falls back to its built-in defaults
      }
    }
    load('/api/diseases', setAvailableDiseases, 'diseases')
    load('/api/networks', setAvailableNetworks, 'networks')
  }, [])

  const isRunning =
    simulationStatus?.status === 'initializing' || simulationStatus?.status === 'running'

  // Poll for progress. This has to cover 'initializing' as well as 'running':
  // the backend reports 'initializing' for the first moments of a run, and
  // polling only on 'running' meant the very first poll cleared the interval
  // and the UI hung at 0% forever.
  useEffect(() => {
    if (!currentSimulation || !isRunning) return

    let cancelled = false
    const poll = async () => {
      try {
        const response = await fetch(apiUrl(`/api/simulation/${currentSimulation}/status`))
        if (!response.ok) throw new Error('Could not reach the simulation server')
        const data = await response.json()
        if (!cancelled) setSimulationStatus(data)
      } catch (err) {
        if (!cancelled) setError(err.message)
      }
    }

    poll()
    const interval = setInterval(poll, POLL_INTERVAL_MS)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [currentSimulation, isRunning])

  // Fetch results once the run completes
  useEffect(() => {
    if (simulationStatus?.status === 'failed') {
      setError(`Simulation failed: ${simulationStatus.error || 'unknown error'}`)
      return
    }

    if (simulationStatus?.status !== 'completed' || !currentSimulation) return
    if (fetchedResultsFor.current === currentSimulation) return
    fetchedResultsFor.current = currentSimulation

    const fetchResults = async () => {
      try {
        const response = await fetch(apiUrl(`/api/simulation/${currentSimulation}/results`))
        if (!response.ok) throw new Error('Could not load simulation results')
        setSimulationResults(await response.json())
        setActiveTab('analysis')
      } catch (err) {
        setError(err.message)
      }
    }
    fetchResults()
  }, [simulationStatus, currentSimulation])

  const handleStartSimulation = useCallback(async (config) => {
    setStarting(true)
    setError(null)
    setSimulationResults(null)
    fetchedResultsFor.current = null

    try {
      const response = await fetch(apiUrl('/api/simulation'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })

      if (!response.ok) {
        // FastAPI validation errors arrive as a structured detail list
        const problem = await response.json().catch(() => null)
        const detail = problem?.detail
        throw new Error(
          Array.isArray(detail)
            ? detail.map((d) => `${d.loc?.slice(1).join('.')}: ${d.msg}`).join('; ')
            : detail || 'Failed to start simulation'
        )
      }

      const data = await response.json()
      setCurrentSimulation(data.simulation_id)
      setSimulationStatus({
        status: 'initializing',
        current_day: 0,
        total_days: config.simulation_days,
        progress: 0,
      })
      setActiveTab('simulation')
    } catch (err) {
      setError(err.message)
    } finally {
      setStarting(false)
    }
  }, [])

  const handleRunExample = useCallback(() => {
    handleStartSimulation({
      network: { population: 800, network_type: 'hybrid' },
      disease: { variant: 'delta' },
      n_seed_infections: 5,
      seed_method: 'random',
      simulation_days: 120,
      intervention_scenario: 'rapid_response',
      vaccination_rate: 0.02,
      compliance_rate: 0.75,
      custom_interventions: [],
    })
  }, [handleStartSimulation])

  const handleNewSimulation = useCallback(() => {
    setCurrentSimulation(null)
    setSimulationStatus(null)
    setSimulationResults(null)
    setError(null)
    fetchedResultsFor.current = null
    setActiveTab('simulation')
  }, [])

  const detailed = simulationResults?.detailed_data
  const history = simulationResults?.history

  const statusLabel = useMemo(() => {
    if (isRunning) return { text: 'Running', className: 'text-amber-400' }
    if (simulationStatus?.status === 'failed') return { text: 'Failed', className: 'text-red-400' }
    if (simulationResults) return { text: 'Ready', className: 'text-emerald-400' }
    return { text: 'Idle', className: 'text-gray-400' }
  }, [isRunning, simulationStatus, simulationResults])

  return (
    <div className="min-h-screen bg-gray-950">
      <header className="bg-gray-900 border-b border-gray-800">
        <div className="max-w-[1600px] mx-auto px-6 py-5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <span className="text-4xl" aria-hidden="true">🦠</span>
            <div>
              <h1 className="text-2xl font-bold text-white">EpiVirus Simulator</h1>
              <p className="text-gray-400 text-sm">Network-based epidemic modelling</p>
            </div>
          </div>
          <div className="bg-gray-800 px-4 py-2 rounded-lg border border-gray-700 text-sm">
            <span className="text-gray-400">Status: </span>
            <span className={`font-semibold ${statusLabel.className}`}>{statusLabel.text}</span>
          </div>
        </div>
      </header>

      <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
        <div className="max-w-[1600px] mx-auto px-6 flex gap-1 overflow-x-auto">
          {TABS.map((tab) => (
            <TabButton
              key={tab.id}
              active={activeTab === tab.id}
              disabled={tab.needsResults && !simulationResults}
              onClick={() => setActiveTab(tab.id)}
              icon={tab.icon}
              label={tab.label}
            />
          ))}
        </div>
      </nav>

      <main className="max-w-[1600px] mx-auto px-6 py-8">
        {error && (
          <div className="bg-red-950 border border-red-800 text-red-200 px-5 py-4 rounded-lg mb-6 flex items-start gap-3">
            <span aria-hidden="true">⚠️</span>
            <span className="flex-1">{error}</span>
            <button
              type="button"
              onClick={() => setError(null)}
              className="text-red-300 hover:text-white"
              aria-label="Dismiss error"
            >
              ✕
            </button>
          </div>
        )}

        {activeTab === 'overview' && (
          <OverviewTab
            hasSimulation={Boolean(currentSimulation)}
            results={simulationResults}
            isRunning={isRunning}
            onRunExample={handleRunExample}
            onNewSimulation={handleNewSimulation}
            onGoToSimulation={() => setActiveTab('simulation')}
          />
        )}

        {activeTab === 'simulation' && (
          <div className="space-y-6">
            <SimulationConfig
              diseases={availableDiseases}
              networks={availableNetworks}
              onStartSimulation={handleStartSimulation}
              loading={starting}
              running={isRunning}
            />

            {isRunning && simulationStatus && (
              <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg space-y-4">
                <div className="flex justify-between text-sm text-gray-300">
                  <span>
                    Day {simulationStatus.current_day} of {simulationStatus.total_days}
                  </span>
                  <span className="tabular-nums">{Math.round(simulationStatus.progress)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-indigo-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${simulationStatus.progress}%` }}
                  />
                </div>
                {simulationStatus.network_info ? (
                  <NetworkInfo info={simulationStatus.network_info} />
                ) : (
                  <LoadingSpinner message="Building the contact network…" />
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'analysis' && simulationResults && (
          <div className="space-y-8">
            <SimulationResults results={simulationResults} />

            <ChartSection title="Epidemic dynamics">
              <SeirdDynamicsChart history={history} />
              <PopulationCompositionChart history={history} />
              <EpidemicCurveChart
                dailyNewCases={detailed?.daily_new_cases}
                time={history?.time}
              />
              <REffectiveChart rEffective={detailed?.r_effective} time={history?.time} />
            </ChartSection>

            <ChartSection title="Health outcomes">
              <HealthcareBurdenChart
                severity={detailed?.severity_breakdown}
                capacity={detailed?.hospital_capacity?.capacity}
                time={history?.time}
              />
              <DailyDeathsChart dailyDeaths={detailed?.daily_deaths} time={history?.time} />
              <CumulativeOutcomesChart
                history={history}
                cumulativeCases={detailed?.cumulative_cases}
              />
              <AgeDistributionChart ageDistribution={detailed?.age_distribution} />
            </ChartSection>

            <ChartSection title="Network structure">
              <DegreeDistributionChart degreeDistribution={detailed?.degree_distribution} />
              <MobilityDistributionChart mobilityDistribution={detailed?.mobility_distribution} />
              <SocialClusteringChart clustering={detailed?.social_clustering} />
            </ChartSection>
          </div>
        )}

        {activeTab === 'network' && simulationResults && (
          <NetworkView simulationId={currentSimulation} history={history} />
        )}

        {activeTab === 'results' && simulationResults && (
          <ResultsTab results={simulationResults} />
        )}
      </main>

      <footer className="border-t border-gray-800 mt-12 py-6 text-center text-gray-500 text-sm">
        EpiVirus · Network-based epidemic modelling
      </footer>
    </div>
  )
}

function ChartSection({ title, children }) {
  return (
    <section>
      <h2 className="text-xl font-bold text-white mb-4">{title}</h2>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">{children}</div>
    </section>
  )
}

function TabButton({ active, onClick, icon, label, disabled }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={disabled ? 'Run a simulation first' : undefined}
      className={`px-5 py-3.5 font-semibold whitespace-nowrap border-b-2 transition-colors ${
        active
          ? 'border-indigo-500 text-white'
          : disabled
            ? 'border-transparent text-gray-600 cursor-not-allowed'
            : 'border-transparent text-gray-400 hover:text-gray-200'
      }`}
    >
      <span className="mr-2" aria-hidden="true">{icon}</span>
      {label}
    </button>
  )
}

function ResultsTab({ results }) {
  const { summary = {}, history = {}, config = {} } = results

  const rows = useMemo(
    () =>
      (history.time ?? []).map((day, i) => ({
        day,
        S: history.S?.[i] ?? 0,
        E: history.E?.[i] ?? 0,
        I: history.I?.[i] ?? 0,
        R: history.R?.[i] ?? 0,
        D: history.D?.[i] ?? 0,
        V: history.V?.[i] ?? 0,
      })),
    [history]
  )

  const metrics = [
    ['Initial population', summary.initial_population],
    ['Total infected', summary.total_infected],
    ['Total recovered', summary.total_recovered],
    ['Total deaths', summary.total_deaths],
    ['Total hospitalised', summary.total_hospitalized],
    ['Total vaccinated', summary.total_vaccinated],
    ['Final susceptible', summary.final_susceptible],
    ['Peak infections', summary.peak_infections],
    ['Peak day', summary.peak_day],
    ['Attack rate', `${((summary.attack_rate ?? 0) * 100).toFixed(1)}%`],
    ['Case fatality rate', `${((summary.case_fatality_rate ?? 0) * 100).toFixed(2)}%`],
    ['Final R effective', (summary.final_r_effective ?? 0).toFixed(2)],
  ]

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <h2 className="text-xl font-bold text-white">Full results</h2>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => exportCSV(rows)}
              className="px-4 py-2 rounded-lg font-semibold text-white bg-emerald-700 hover:bg-emerald-600 transition-colors"
            >
              Export CSV
            </button>
            <button
              type="button"
              onClick={() => exportJSON(results)}
              className="px-4 py-2 rounded-lg font-semibold text-white bg-indigo-600 hover:bg-indigo-500 transition-colors"
            >
              Export JSON
            </button>
          </div>
        </div>

        <dl className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {metrics.map(([label, value]) => (
            <div key={label} className="bg-gray-900 rounded-lg border border-gray-700 p-4">
              <dt className="text-xs text-gray-400 uppercase tracking-wide">{label}</dt>
              <dd className="text-xl font-bold text-white mt-1 tabular-nums">{value ?? 0}</dd>
            </div>
          ))}
        </dl>

        <div className="mt-6 text-sm text-gray-400">
          {config.network?.population} people · {config.network?.network_type} network ·{' '}
          {config.disease?.variant} · {config.intervention_scenario?.replace(/_/g, ' ')}
        </div>
      </div>

      {/* The table view that the charts' accessibility fallback depends on */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg">
        <h2 className="text-xl font-bold text-white mb-1">Daily time series</h2>
        <p className="text-sm text-gray-400 mb-4">
          Every value plotted in the Analysis tab, in full.
        </p>
        <div className="overflow-auto max-h-[28rem] rounded-lg border border-gray-700">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-900 sticky top-0">
              <tr>
                {['Day', 'Susceptible', 'Exposed', 'Infectious', 'Recovered', 'Deceased', 'Vaccinated'].map((head) => (
                  <th key={head} className="px-4 py-3 text-left font-semibold text-gray-300 whitespace-nowrap">
                    {head}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {rows.map((row) => (
                <tr key={row.day} className="hover:bg-gray-700/40">
                  <td className="px-4 py-2 text-white tabular-nums">{row.day}</td>
                  <td className="px-4 py-2 text-gray-300 tabular-nums">{row.S}</td>
                  <td className="px-4 py-2 text-gray-300 tabular-nums">{row.E}</td>
                  <td className="px-4 py-2 text-gray-300 tabular-nums">{row.I}</td>
                  <td className="px-4 py-2 text-gray-300 tabular-nums">{row.R}</td>
                  <td className="px-4 py-2 text-gray-300 tabular-nums">{row.D}</td>
                  <td className="px-4 py-2 text-gray-300 tabular-nums">{row.V}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function download(content, type, extension) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `epivirus_results_${Date.now()}.${extension}`
  anchor.click()
  URL.revokeObjectURL(url)
}

function exportCSV(rows) {
  if (!rows.length) return
  const headers = ['day', 'S', 'E', 'I', 'R', 'D', 'V']
  const csv = [
    headers.join(','),
    ...rows.map((row) => headers.map((h) => row[h === 'day' ? 'day' : h]).join(',')),
  ].join('\n')
  download(csv, 'text/csv', 'csv')
}

function exportJSON(results) {
  download(JSON.stringify(results, null, 2), 'application/json', 'json')
}

export default App
