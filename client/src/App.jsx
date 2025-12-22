// src/App.jsx - Main EpiVirus Frontend Application
import { useState, useEffect } from 'react'
import './App.css'

// Import components
import Header from './components/Header'
import SimulationConfig from './components/SimulationConfig'
import SimulationResults from './components/SimulationResults'
import NetworkInfo from './components/NetworkInfo'
import EpidemicChart from './components/EpidemicChart'
import LoadingSpinner from './components/LoadingSpinner'
import OverviewTab from './components/OverviewTab'
import AnimationTab from './components/AnimationTab'
import {
  DiseaseDynamicsChart,
  DailyNewCasesChart,
  AgeDistributionChart,
  DegreeDistributionChart
} from './components/AdvancedCharts'
import {
  DiseaseDynamicsStacked,
  EpidemicCurveChart,
  HealthcareSystemChart,
  SimulationSummary,
  SEIRDDynamicsChart,
  DailyNewCasesBar,
  IntegratedRiskModel,
  AgeDistributionInfections,
  DegreeDistributionBar,
  AgeDistributionBarGreen,
  MobilityDistributionPie,
  SocialClusteringPie,
  SEIRDynamicsChart,
  DailyNewInfectionsChart,
  StackedAreaChart,
  SeverityBreakdownChart,
  AgeDistributionPie,
  AgeDistributionBar,
  DegreeDistributionChart as DegreeDistChart,
  REffectiveChart,
  CumulativeStatsChart,
  AttackRateChart,
  ActiveVsRecoveredChart,
  InfectionRateIndicator,
  MobilityDistributionChart,
  SocialClusteringChart,
  HospitalCapacityChart,
  InfectionWaveChart,
  PopulationStateTreemap,
  AgeInfectionScatter,
  DegreeDistributionRadial
} from './components/ComprehensiveCharts'
import Network3D from './components/Network3D'

function App() {
  const [simulations, setSimulations] = useState([])
  const [currentSimulation, setCurrentSimulation] = useState(null)
  const [simulationStatus, setSimulationStatus] = useState(null)
  const [simulationResults, setSimulationResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [availableDiseases, setAvailableDiseases] = useState([])
  const [availableNetworks, setAvailableNetworks] = useState([])
  const [activeTab, setActiveTab] = useState('overview') // Main tabs: overview, simulation, analysis, visualization, animation, results
  const [visualizationMode, setVisualizationMode] = useState('2d') // '2d' or '3d'

  // Fetch available diseases and networks on mount
  useEffect(() => {
    fetchDiseases()
    fetchNetworks()
    fetchSimulations()
  }, [])

  // Poll for simulation status updates
  useEffect(() => {
    if (currentSimulation && simulationStatus?.status === 'running') {
      const interval = setInterval(() => {
        fetchSimulationStatus(currentSimulation)
      }, 2000)

      return () => clearInterval(interval)
    }
  }, [currentSimulation, simulationStatus?.status])

  // Fetch simulation results when completed
  useEffect(() => {
    if (simulationStatus?.status === 'completed') {
      fetchSimulationResults(currentSimulation)
    } else if (simulationStatus?.status === 'failed') {
      setError(`Simulation failed: ${simulationStatus.error || 'Unknown error'}`)
      setLoading(false)
      console.error('Simulation error details:', simulationStatus)
    }
  }, [simulationStatus?.status])

  const fetchDiseases = async () => {
    try {
      const response = await fetch('/api/diseases')
      const data = await response.json()
      setAvailableDiseases(data.diseases)
    } catch (err) {
      console.error('Failed to fetch diseases:', err)
    }
  }

  const fetchNetworks = async () => {
    try {
      const response = await fetch('/api/networks')
      const data = await response.json()
      setAvailableNetworks(data.networks)
    } catch (err) {
      console.error('Failed to fetch networks:', err)
    }
  }

  const fetchSimulations = async () => {
    try {
      const response = await fetch('/api/simulations')
      const data = await response.json()
      setSimulations(data.simulations)
    } catch (err) {
      console.error('Failed to fetch simulations:', err)
    }
  }

  const fetchSimulationStatus = async (simId) => {
    try {
      const response = await fetch(`/api/simulation/${simId}/status`)
      const data = await response.json()
      setSimulationStatus(data)
    } catch (err) {
      console.error('Failed to fetch status:', err)
    }
  }

  const fetchSimulationResults = async (simId) => {
    try {
      const response = await fetch(`/api/simulation/${simId}/results`)
      const data = await response.json()
      console.log('🔍 Simulation Results Data:', data)
      console.log('📊 Detailed Data:', data.detailed_data)
      console.log('📈 Degree Distribution:', data.detailed_data?.degree_distribution)
      console.log('👥 Age Distribution:', data.detailed_data?.age_distribution)
      console.log('🚶 Mobility Distribution:', data.detailed_data?.mobility_distribution)
      console.log('🔗 Social Clustering:', data.detailed_data?.social_clustering)
      setSimulationResults(data)
    } catch (err) {
      console.error('Failed to fetch results:', err)
      setError('Failed to fetch simulation results')
    }
  }

  const handleStartSimulation = async (config) => {
    setLoading(true)
    setError(null)
    setSimulationResults(null)

    try {
      const response = await fetch('/api/simulation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      })

      if (!response.ok) {
        throw new Error('Failed to start simulation')
      }

      const data = await response.json()
      setCurrentSimulation(data.simulation_id)
      setSimulationStatus({
        status: 'running',
        current_day: 0,
        total_days: config.simulation_days,
        progress: 0,
      })

      // Refresh simulations list
      fetchSimulations()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteSimulation = async (simId) => {
    try {
      await fetch(`/api/simulation/${simId}`, {
        method: 'DELETE',
      })

      // Clear if it's the current simulation
      if (simId === currentSimulation) {
        setCurrentSimulation(null)
        setSimulationStatus(null)
        setSimulationResults(null)
      }

      // Refresh list
      fetchSimulations()
    } catch (err) {
      console.error('Failed to delete simulation:', err)
    }
  }

  const handleRunExample = async () => {
    // Simplified example config
    const exampleConfig = {
      network: { population: 500, network_type: 'hybrid' },
      disease: { variant: 'omicron' },
      n_seed_infections: 5,
      simulation_days: 90,
      intervention_scenario: 'rapid_response',
      vaccination_rate: 0.01,
      compliance_rate: 0.7,
      animate: true,
      animation_step: 2
    }
    await handleStartSimulation(exampleConfig)
    setActiveTab('simulation')
  }

  const handlePrepareAnimation = () => {
    // Placeholder - implement animation preparation
    alert('Animation preparation feature coming soon!')
  }

  const handleNewSimulation = () => {
    setCurrentSimulation(null)
    setSimulationStatus(null)
    setSimulationResults(null)
    setError(null)
    setActiveTab('simulation')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-950">
      {/* Modern Header */}
      <div className="bg-gray-800 shadow-2xl border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-gray-700 p-3 rounded-xl shadow-lg">
                <span className="text-4xl">🦠</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white drop-shadow-lg">EpiVirus Simulator</h1>
                <p className="text-gray-300 text-sm">Advanced Disease Spread Modeling & Analysis</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="bg-gray-800 px-4 py-2 rounded-lg border border-gray-700">
                <span className="text-gray-300 text-sm font-medium">Status: </span>
                <span className={`font-bold ${simulationStatus?.status === 'running' ? 'text-yellow-400' :
                  simulationResults ? 'text-green-400' : 'text-gray-400'
                  }`}>
                  {simulationStatus?.status === 'running' ? '⚡ Running' :
                    simulationResults ? '✓ Ready' : '○ Waiting'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Tab Navigation */}
      <div className="bg-gray-900 shadow-lg sticky top-0 z-40 border-b-2 border-gray-800">
        <div className="mx-auto px-4" style={{ maxWidth: '95%' }}>
          <div className="flex space-x-1 overflow-x-auto py-2">
            <TabButton
              active={activeTab === 'overview'}
              onClick={() => setActiveTab('overview')}
              icon="🏠"
              label="Overview"
            />
            <TabButton
              active={activeTab === 'simulation'}
              onClick={() => setActiveTab('simulation')}
              icon="⚙️"
              label="Simulation"
            />
            <TabButton
              active={activeTab === 'analysis'}
              onClick={() => setActiveTab('analysis')}
              icon="📊"
              label="Analysis"
              disabled={!simulationResults}
            />
            <TabButton
              active={activeTab === 'visualization'}
              onClick={() => setActiveTab('visualization')}
              icon="🎨"
              label="Visualization"
              disabled={!simulationResults}
            />
            <TabButton
              active={activeTab === 'animation'}
              onClick={() => setActiveTab('animation')}
              icon="🎬"
              label="Animation"
              disabled={!simulationResults}
            />
            <TabButton
              active={activeTab === 'results'}
              onClick={() => setActiveTab('results')}
              icon="📈"
              label="Results"
              disabled={!simulationResults}
            />
          </div>
        </div>
      </div>

      <main className="mx-auto px-4 py-8" style={{ maxWidth: '95%' }}>
        {/* Error Display */}
        {error && (
          <div className="bg-red-500 text-white px-6 py-4 rounded-lg mb-6 shadow-lg animate-pulse">
            <div className="flex items-center">
              <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-white hover:text-red-100"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <OverviewTab
            simulator={currentSimulation}
            animationReady={false}
            simulationHistory={simulationResults}
            simulationComplete={simulationStatus?.status === 'completed'}
            animationFrames={[]}
            onRunExample={handleRunExample}
            onPrepareAnimation={handlePrepareAnimation}
            onNewSimulation={handleNewSimulation}
          />
        )}

        {activeTab === 'simulation' && (
          <div className="space-y-4">
            {/* Simulation Configuration Section */}
            <div className="bg-gray-800 rounded-lg shadow-xl p-6">
              <h2 className="text-2xl font-bold mb-4 text-white border-b border-gray-700 pb-3">🛠️ Simulation Configuration</h2>
              <SimulationConfig
                diseases={availableDiseases}
                networks={availableNetworks}
                onStartSimulation={handleStartSimulation}
                loading={loading}
                currentStatus={simulationStatus}
              />
            </div>

            {/* Status Row */}
            {(simulationStatus?.status === 'running' || loading) && (
              <div className="grid grid-cols-1 gap-4">
                {/* Simulation Progress */}
                {simulationStatus && simulationStatus.status === 'running' && (
                  <div className="bg-gray-800 rounded-lg shadow-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-white border-b border-gray-700 pb-2">⚡ Progress</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between text-sm text-gray-300 mb-2">
                        <span>Day {simulationStatus.current_day} of {simulationStatus.total_days}</span>
                        <span>{Math.round(simulationStatus.progress)}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-purple-600 h-4 rounded-full transition-all duration-500"
                          style={{ width: `${simulationStatus.progress}%` }}
                        />
                      </div>
                      {simulationStatus.network_info && (
                        <NetworkInfo info={simulationStatus.network_info} />
                      )}
                    </div>
                  </div>
                )}

                {/* Loading Indicator */}
                {loading && (
                  <div className="bg-gray-800 rounded-lg shadow-xl p-6">
                    <LoadingSpinner message="Initializing simulation..." />
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Analysis Tab */}
        {activeTab === 'analysis' && simulationResults && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg shadow-xl p-6">
              <h2 className="text-3xl font-bold mb-6 text-white">📊 Simulation Analysis</h2>

              {/* Analysis Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Disease Dynamics */}
                {simulationResults.history && (
                  <>
                    <DiseaseDynamicsStacked history={simulationResults.history} />
                    <EpidemicCurveChart history={simulationResults.history} />
                    <SEIRDDynamicsChart history={simulationResults.history} />
                    <DailyNewCasesBar history={simulationResults.history} />
                  </>
                )}
              </div>

              {/* Network Metrics */}
              <div className="mt-6">
                <h3 className="text-xl font-bold text-white mb-4">Network Analysis</h3>
                <div className="grid grid-cols-1 gap-6">
                  {simulationResults.detailed_data?.degree_distribution && (
                    <DegreeDistributionBar degreeData={simulationResults.detailed_data.degree_distribution} />
                  )}
                  {simulationResults.detailed_data?.age_distribution && (
                    <AgeDistributionBarGreen ageData={simulationResults.detailed_data.age_distribution} />
                  )}
                </div>
              </div>

              {/* Detailed Statistics */}
              <div className="mt-6 bg-gradient-to-r from-blue-900 to-purple-900 bg-opacity-40 p-6 rounded-lg">
                <h3 className="text-xl font-bold text-white mb-4">📈 Key Metrics</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <MetricCard
                    label="Attack Rate"
                    value={`${((simulationResults.summary?.attack_rate || 0) * 100).toFixed(1)}%`}
                    icon="🎯"
                  />
                  <MetricCard
                    label="Peak Infections"
                    value={simulationResults.summary?.peak_infections || 0}
                    icon="📈"
                  />
                  <MetricCard
                    label="Total Deaths"
                    value={simulationResults.summary?.total_deaths || 0}
                    icon="💀"
                    color="red"
                  />
                  <MetricCard
                    label="Case Fatality Rate"
                    value={`${((simulationResults.summary?.case_fatality_rate || 0) * 100).toFixed(2)}%`}
                    icon="💔"
                    color="red"
                  />
                  <MetricCard
                    label="R Effective"
                    value={(simulationResults.summary?.final_r_effective || 0).toFixed(2)}
                    icon="🔄"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Visualization Tab */}
        {activeTab === 'visualization' && simulationResults && (
          <div className="space-y-6">
            {/* Visualization Mode Selector */}
            <div className="bg-gray-800 rounded-lg shadow-xl p-4">
              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => setVisualizationMode('2d')}
                  className={`px-8 py-3 rounded-lg font-semibold transition-all ${visualizationMode === '2d'
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                >
                  📊 2D Charts & Statistics
                </button>
                <button
                  onClick={() => setVisualizationMode('3d')}
                  className={`px-8 py-3 rounded-lg font-semibold transition-all ${visualizationMode === '3d'
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                >
                  🌐 3D Network Simulation
                </button>
              </div>
            </div>

            {/* 2D Charts Tab */}
            {visualizationMode === '2d' && (
              <div className="space-y-6">
                {/* PRIMARY BACKEND-STYLE CHARTS (Top Priority) */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Disease Dynamics Over Time */}
                  {simulationResults.history && (
                    <DiseaseDynamicsStacked history={simulationResults.history} />
                  )}

                  {/* Epidemic Curve */}
                  {simulationResults.history && (
                    <EpidemicCurveChart history={simulationResults.history} />
                  )}

                  {/* Healthcare System Burden */}
                  {simulationResults.detailed_data?.severity_breakdown && (
                    <HealthcareSystemChart
                      severityData={simulationResults.detailed_data.severity_breakdown}
                      capacity={simulationResults.detailed_data.hospital_capacity?.capacity || 50}
                    />
                  )}

                  {/* Simulation Summary */}
                  {simulationResults && (
                    <SimulationSummary simulationResults={simulationResults} />
                  )}
                </div>

                {/* SECOND ROW - More Backend-Style Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* SEIRD Dynamics (5 lines) */}
                  {simulationResults.history && (
                    <SEIRDDynamicsChart history={simulationResults.history} />
                  )}

                  {/* Daily New Cases */}
                  {simulationResults.history && (
                    <DailyNewCasesBar history={simulationResults.history} />
                  )}

                  {/* Age Distribution of Infections */}
                  {simulationResults.detailed_data?.age_distribution && (
                    <AgeDistributionInfections ageData={simulationResults.detailed_data.age_distribution} />
                  )}
                </div>

                {/* NETWORK AND DEMOGRAPHIC METRICS SECTION */}
                <div className="bg-gray-700 p-4 rounded-lg">
                  <h2 className="text-3xl font-bold text-center mb-6 text-white">Network and Demographic Metrics</h2>
                  <div className="grid grid-cols-1 gap-6">
                    {/* Degree Distribution - Bar Graph (Blue) - Full Width */}
                    {simulationResults.detailed_data?.degree_distribution ? (
                      <DegreeDistributionBar degreeData={simulationResults.detailed_data.degree_distribution} />
                    ) : (
                      <div className="bg-gray-800 rounded-lg shadow-xl p-6">
                        <h3 className="text-xl font-bold text-center text-gray-400">Degree Distribution</h3>
                        <p className="text-center text-gray-400 mt-4">No data available</p>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">

                    {/* Age Distribution - Bar Graph (Green) */}
                    {simulationResults.detailed_data?.age_distribution ? (
                      <AgeDistributionBarGreen ageData={simulationResults.detailed_data.age_distribution} />
                    ) : (
                      <div className="bg-gray-800 rounded-lg shadow-xl p-6">
                        <h3 className="text-xl font-bold text-center text-gray-400">Age Distribution</h3>
                        <p className="text-center text-gray-400 mt-4">No data available</p>
                      </div>
                    )}

                    {/* Mobility Distribution - Pie Chart (Orange) */}
                    {simulationResults.detailed_data?.mobility_distribution ? (
                      <MobilityDistributionPie mobilityData={simulationResults.detailed_data.mobility_distribution} />
                    ) : (
                      <div className="bg-gray-800 rounded-lg shadow-xl p-6">
                        <h3 className="text-xl font-bold text-center text-gray-400">Mobility Distribution</h3>
                        <p className="text-center text-gray-400 mt-4">No data available</p>
                      </div>
                    )}

                    {/* Social Clustering - Pie Chart (Purple) */}
                    {simulationResults.detailed_data?.social_clustering ? (
                      <SocialClusteringPie clusteringData={simulationResults.detailed_data.social_clustering} />
                    ) : (
                      <div className="bg-gray-800 rounded-lg shadow-xl p-6">
                        <h3 className="text-xl font-bold text-center text-gray-400">Social Clustering by Age</h3>
                        <p className="text-center text-gray-400 mt-4">No data available</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Original Advanced Charts */}
                {simulationResults.history && (
                  <>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <CumulativeStatsChart history={simulationResults.history} />
                      <AttackRateChart history={simulationResults.history} />
                    </div>
                    <ActiveVsRecoveredChart history={simulationResults.history} />
                  </>
                )}

                {/* Demographics & Network Analysis */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {simulationResults.detailed_data?.age_distribution && (
                    <>
                      <AgeDistributionPie ageData={simulationResults.detailed_data.age_distribution} />
                      <AgeDistributionBar ageData={simulationResults.detailed_data.age_distribution} />
                      <AgeDistributionChart ageData={simulationResults.detailed_data.age_distribution} />
                    </>
                  )}

                  {/* NEW: Mobility Distribution (Backend-matching) */}
                  {simulationResults.detailed_data?.mobility_distribution && (
                    <MobilityDistributionChart mobilityData={simulationResults.detailed_data.mobility_distribution} />
                  )}

                  {/* NEW: Social Clustering by Age (Backend-matching) */}
                  {simulationResults.detailed_data?.social_clustering && (
                    <SocialClusteringChart clusteringData={simulationResults.detailed_data.social_clustering} />
                  )}

                  {/* NEW: Age vs Infection Scatter Plot */}
                  {simulationResults.detailed_data?.age_distribution && simulationResults.detailed_data?.degree_distribution && (
                    <AgeInfectionScatter
                      ageData={simulationResults.detailed_data.age_distribution}
                      degreeData={simulationResults.detailed_data.degree_distribution}
                    />
                  )}
                </div>

                {/* NEW: Hospital Capacity Timeline (Backend-matching) */}
                {simulationResults.detailed_data?.severity_breakdown && (
                  <HospitalCapacityChart
                    hospitalData={simulationResults.detailed_data.severity_breakdown}
                    capacity={simulationResults.detailed_data.hospital_capacity?.capacity || 100}
                  />
                )}

                {/* Infection Wave Analysis and Population Treemap - Side by Side */}
                {simulationResults.history && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <InfectionWaveChart history={simulationResults.history} />
                    <PopulationStateTreemap history={simulationResults.history} />
                  </div>
                )}

                {/* R-Effective and Epidemic Chart - Side by Side */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {simulationResults.detailed_data?.r_effective && (
                    <REffectiveChart rEffectiveHistory={simulationResults.detailed_data.r_effective} />
                  )}
                  <EpidemicChart history={simulationResults.history} />
                </div>
              </div>
            )}

            {/* 3D Network Visualization Tab */}
            {visualizationMode === '3d' && (
              <div className="space-y-6">
                <Network3D simulationData={simulationResults} />
              </div>
            )}
          </div>
        )}

        {/* Animation Tab */}
        {activeTab === 'animation' && (
          <AnimationTab simulationResults={simulationResults} />
        )}

        {/* Results Tab */}
        {activeTab === 'results' && simulationResults && (
          <div className="space-y-6">
            {/* Simulation Results Summary */}
            <div className="bg-gray-800 rounded-lg shadow-xl p-6">
              <h2 className="text-2xl font-bold mb-4 text-white border-b border-gray-700 pb-3">📊 Results Summary</h2>
              <SimulationResults results={simulationResults} />
            </div>

            <div className="bg-gray-800 rounded-lg shadow-xl p-6">
              <h2 className="text-3xl font-bold mb-6 text-white">📈 Detailed Results & Export</h2>

              {/* Export Options */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <button
                  onClick={() => exportCSV(simulationResults)}
                  className="py-3 px-4 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-all shadow-lg"
                >
                  📊 Export CSV
                </button>
                <button
                  onClick={() => exportJSON(simulationResults)}
                  className="py-3 px-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all shadow-lg"
                >
                  📋 Export JSON
                </button>
              </div>

              {/* Detailed Metrics */}
              <div className="bg-gradient-to-r from-blue-900 to-purple-900 bg-opacity-40 p-6 rounded-lg mb-6">
                <h3 className="text-xl font-semibold text-white mb-4">📋 Detailed Metrics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <DetailMetric label="Initial Population" value={simulationResults.summary?.initial_population || 0} />
                  <DetailMetric label="Total Infected" value={simulationResults.summary?.total_infected || 0} />
                  <DetailMetric label="Total Recovered" value={simulationResults.summary?.total_recovered || 0} />
                  <DetailMetric label="Total Deaths" value={simulationResults.summary?.total_deaths || 0} />
                  <DetailMetric label="Final Susceptible" value={simulationResults.summary?.final_susceptible || 0} />
                  <DetailMetric label="Total Vaccinated" value={simulationResults.summary?.total_vaccinated || 0} />
                  <DetailMetric label="Peak Day" value={simulationResults.summary?.peak_day || 0} />
                  <DetailMetric label="Peak Infections" value={simulationResults.summary?.peak_infections || 0} />
                  <DetailMetric label="Attack Rate" value={`${((simulationResults.summary?.attack_rate || 0) * 100).toFixed(1)}%`} />
                  <DetailMetric label="Case Fatality Rate" value={`${((simulationResults.summary?.case_fatality_rate || 0) * 100).toFixed(2)}%`} />
                  <DetailMetric label="R Effective (Final)" value={(simulationResults.summary?.final_r_effective || 0).toFixed(2)} />
                  <DetailMetric label="Total Hospitalized" value={simulationResults.summary?.total_hospitalized || 0} />
                </div>
              </div>

              {/* Time Series Data Table */}
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-white mb-4">📈 Time Series Data</h3>
                <div className="overflow-x-auto max-h-96">
                  <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-700 sticky top-0">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">Day</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">S</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">E</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">I</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">R</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">D</th>
                      </tr>
                    </thead>
                    <tbody className="bg-gray-800 divide-y divide-gray-700">
                      {simulationResults.history?.time?.slice(-30).map((day, idx) => (
                        <tr key={idx} className="hover:bg-gray-700">
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-white">{day}</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-300">{simulationResults.history.S[idx]}</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-300">{simulationResults.history.E?.[idx] || 0}</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-300">{simulationResults.history.I[idx]}</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-300">{simulationResults.history.R[idx]}</td>
                          <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-300">{simulationResults.history.D?.[idx] || 0}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-gray-400 mt-2">Showing last 30 days of simulation</p>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="bg-gray-900/50 backdrop-blur-sm mt-12 py-6 text-center text-gray-400 border-t border-gray-800">
        <p className="text-sm">
          EpiVirus Pandemic Simulation Platform • Network-Based Epidemic Modeling
        </p>
      </footer>
    </div>
  )
}

// Helper Components
function TabButton({ active, onClick, icon, label, disabled = false }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`relative px-6 py-4 font-bold transition-all duration-300 whitespace-nowrap transform ${active
        ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-xl scale-105 rounded-t-lg'
        : disabled
          ? 'bg-gray-800 text-gray-300 cursor-not-allowed opacity-60'
          : 'bg-transparent text-gray-300 hover:bg-gradient-to-r hover:from-gray-800 hover:to-gray-700 hover:shadow-md rounded-t-lg hover:scale-102'
        }`}
    >
      <div className="flex items-center gap-2">
        <span className="text-xl">{icon}</span>
        <span>{label}</span>
      </div>
      {active && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-white rounded-full"></div>
      )}
    </button>
  )
}

function MetricCard({ label, value, icon, color = 'blue' }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    red: 'from-red-500 to-red-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
    indigo: 'from-indigo-500 to-indigo-600',
    pink: 'from-pink-500 to-pink-600'
  }

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color] || colorClasses.blue} rounded-2xl p-6 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 cursor-pointer`}>
      <div className="flex items-start justify-between mb-3">
        <div className="text-white text-opacity-90 text-sm font-semibold uppercase tracking-wide">{label}</div>
        <span className="text-4xl opacity-80">{icon}</span>
      </div>
      <div className="text-white text-5xl font-bold drop-shadow-lg">{value}</div>
      <div className="mt-3 h-1.5 bg-white bg-opacity-30 rounded-full overflow-hidden">
        <div className="h-full bg-white rounded-full animate-pulse" style={{ width: '70%' }}></div>
      </div>
    </div>
  )
}

function DetailMetric({ label, value }) {
  // Check if this is a "good zero" metric (deaths, CFR)
  const isDeathMetric = label.toLowerCase().includes('death') || label.toLowerCase().includes('fatality');
  const isZero = value === 0 || value === '0' || value === '0%' || value === '0.00%';
  const isVaccinatedOrHospitalized = label.toLowerCase().includes('vaccinated') || label.toLowerCase().includes('hospitalized');
  
  // Determine styling based on metric type and value
  let valueColorClass = 'text-white';
  let borderClass = 'border-gray-600';
  
  if (isDeathMetric) {
    if (isZero) {
      valueColorClass = 'text-green-400';
      borderClass = 'border-green-600';
    } else {
      valueColorClass = 'text-red-400';
      borderClass = 'border-red-600';
    }
  } else if (isVaccinatedOrHospitalized && isZero) {
    valueColorClass = 'text-gray-400';
  }
  
  return (
    <div className={`bg-gray-700 p-3 rounded border ${borderClass}`}>
      <div className="text-xs text-gray-300 mb-1">{label}</div>
      <div className={`text-lg font-semibold ${valueColorClass}`}>
        {value}
        {isDeathMetric && isZero && <span className="ml-2 text-green-400">✓</span>}
      </div>
    </div>
  )
}

function ConfigDetail({ label, value }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-green-200">
      <span className="text-gray-300 font-medium">{label}:</span>
      <span className="text-gray-300">{value}</span>
    </div>
  )
}

// Export Functions
function exportCSV(results) {
  if (!results?.history) return

  const headers = ['day', 'S', 'E', 'I', 'R', 'D']
  const rows = results.history.time.map((day, idx) => [
    day,
    results.history.S[idx],
    results.history.E?.[idx] || 0,
    results.history.I[idx],
    results.history.R[idx],
    results.history.D?.[idx] || 0
  ])

  const csv = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `simulation_results_${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

function exportJSON(results) {
  const json = JSON.stringify(results, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `simulation_results_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function exportImages(results) {
  alert('Export Images: This feature captures all charts as images. Implementation requires html2canvas library.')
}

function exportAll(results) {
  alert('Export All: This feature creates a ZIP file with all data, charts, and reports. Implementation requires JSZip library.')
}

export default App

