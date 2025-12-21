// components/AnimationTab.jsx
import { useState, useEffect, useRef } from 'react'

export default function AnimationTab({ simulationResults }) {
    const [currentFrame, setCurrentFrame] = useState(0)
    const [isPlaying, setIsPlaying] = useState(false)
    const [playbackSpeed, setPlaybackSpeed] = useState(500)
    const [exportFormat, setExportFormat] = useState('gif')
    const [fps, setFps] = useState(10)
    const [quality, setQuality] = useState('medium')
    const playIntervalRef = useRef(null)

    const maxFrames = simulationResults?.history?.time?.length || 0

    // Auto-play functionality
    useEffect(() => {
        if (isPlaying) {
            playIntervalRef.current = setInterval(() => {
                setCurrentFrame(prev => {
                    if (prev >= maxFrames - 1) {
                        setIsPlaying(false)
                        return 0
                    }
                    return prev + 1
                })
            }, playbackSpeed)
        } else {
            if (playIntervalRef.current) {
                clearInterval(playIntervalRef.current)
            }
        }

        return () => {
            if (playIntervalRef.current) {
                clearInterval(playIntervalRef.current)
            }
        }
    }, [isPlaying, playbackSpeed, maxFrames])

    const handlePlayPause = () => {
        setIsPlaying(!isPlaying)
    }

    const handleFirst = () => {
        setIsPlaying(false)
        setCurrentFrame(0)
    }

    const handlePrev = () => {
        setIsPlaying(false)
        setCurrentFrame(prev => Math.max(0, prev - 1))
    }

    const handleNext = () => {
        setIsPlaying(false)
        setCurrentFrame(prev => Math.min(maxFrames - 1, prev + 1))
    }

    const handleLast = () => {
        setIsPlaying(false)
        setCurrentFrame(maxFrames - 1)
    }

    const handleSliderChange = (e) => {
        setIsPlaying(false)
        setCurrentFrame(parseInt(e.target.value))
    }

    if (!simulationResults) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-400 text-lg">No simulation results available</p>
            </div>
        )
    }

    const currentDay = simulationResults.history?.time?.[currentFrame] || 0
    const currentData = {
        S: simulationResults.history?.S?.[currentFrame] || 0,
        E: simulationResults.history?.E?.[currentFrame] || 0,
        I: simulationResults.history?.I?.[currentFrame] || 0,
        R: simulationResults.history?.R?.[currentFrame] || 0,
        D: simulationResults.history?.D?.[currentFrame] || 0
    }

    return (
        <div className="space-y-6">
            {/* Main Container */}
            <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
                <h2 className="text-3xl font-bold mb-6 text-white flex items-center gap-2">
                    <span>🎬</span>
                    <span>Simulation Animation Viewer</span>
                </h2>

                {/* Top Row - 3D Visualizations Side by Side */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                    <Unique3DVisualization currentData={currentData} currentDay={currentDay} isPlaying={isPlaying} />
                    <NetworkGlobeVisualization
                        currentData={currentData}
                        currentDay={currentDay}
                        isPlaying={isPlaying}
                        simulationResults={simulationResults}
                        currentFrame={currentFrame}
                    />
                </div>

                {/* Middle Row - Frame Controls and Current State Side by Side */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                    {/* Frame-by-Frame Control */}
                    <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <span>▶️</span>
                            <span>Frame Control</span>
                        </h3>

                        {/* Current Frame Info - Compact */}
                        <div className="bg-gray-800 p-3 rounded-lg mb-4">
                            <div className="grid grid-cols-3 gap-2 text-center">
                                <div>
                                    <div className="text-xl font-bold text-blue-400">Day {currentDay}</div>
                                    <div className="text-xs text-gray-400">Current</div>
                                </div>
                                <div>
                                    <div className="text-xl font-bold text-purple-400">
                                        {currentFrame + 1} / {maxFrames}
                                    </div>
                                    <div className="text-xs text-gray-400">Frame</div>
                                </div>
                                <div>
                                    <div className="text-xl font-bold text-green-400">
                                        {Math.round((currentFrame / (maxFrames - 1)) * 100)}%
                                    </div>
                                    <div className="text-xs text-gray-400">Progress</div>
                                </div>
                            </div>
                        </div>

                        {/* Slider */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Timeline: Day {currentDay}
                            </label>
                            <input
                                type="range"
                                min="0"
                                max={Math.max(0, maxFrames - 1)}
                                value={currentFrame}
                                onChange={handleSliderChange}
                                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                            />
                            <div className="flex justify-between text-xs text-gray-400 mt-1">
                                <span>Start</span>
                                <span>Day {simulationResults.history?.time?.[maxFrames - 1] || 0}</span>
                            </div>
                        </div>

                        {/* Control Buttons - Compact */}
                        <div className="grid grid-cols-5 gap-2 mb-4">
                            <button
                                onClick={handleFirst}
                                disabled={currentFrame === 0}
                                className="py-2 px-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-800 disabled:cursor-not-allowed transition-all text-sm"
                            >
                                First
                            </button>
                            <button
                                onClick={handlePrev}
                                disabled={currentFrame === 0}
                                className="py-2 px-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-800 disabled:cursor-not-allowed transition-all text-sm"
                            >
                                Prev
                            </button>
                            <button
                                onClick={handlePlayPause}
                                className={`py-2 px-2 ${isPlaying ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} text-white rounded-lg font-semibold transition-all text-sm`}
                            >
                                {isPlaying ? 'Pause' : 'Play'}
                            </button>
                            <button
                                onClick={handleNext}
                                disabled={currentFrame >= maxFrames - 1}
                                className="py-2 px-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-800 disabled:cursor-not-allowed transition-all text-sm"
                            >
                                Next
                            </button>
                            <button
                                onClick={handleLast}
                                disabled={currentFrame >= maxFrames - 1}
                                className="py-2 px-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-800 disabled:cursor-not-allowed transition-all text-sm"
                            >
                                Last
                            </button>
                        </div>

                        {/* Playback Speed */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Playback Speed: {(1000 / playbackSpeed).toFixed(1)} FPS
                            </label>
                            <div className="grid grid-cols-6 gap-2">
                                {[1, 2, 3, 5, 7, 10].map((fps) => (
                                    <button
                                        key={fps}
                                        onClick={() => setPlaybackSpeed(1000 / fps)}
                                        className={`py-2 px-3 rounded-lg font-semibold transition-all text-sm border ${
                                            Math.abs((1000 / playbackSpeed) - fps) < 0.5
                                                ? 'bg-indigo-600 text-white border-indigo-500'
                                                : 'bg-gray-800 text-gray-300 border-gray-600 hover:bg-gray-700'
                                        }`}
                                    >
                                        {fps}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Live Preview - State Cards */}
                    <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <span>👁️</span>
                            <span>Current State - Day {currentDay}</span>
                        </h3>

                        {/* Visual Bar Chart - Compact */}
                        <div className="bg-gray-800 p-3 rounded-lg">
                            <h4 className="text-sm font-semibold text-gray-300 mb-2">Population Distribution</h4>
                            <div className="space-y-2">
                                <BarRow label="Susceptible" value={currentData.S} max={simulationResults.summary?.initial_population || 1000} color="bg-green-500" />
                                <BarRow label="Exposed" value={currentData.E} max={simulationResults.summary?.initial_population || 1000} color="bg-yellow-500" />
                                <BarRow label="Infected" value={currentData.I} max={simulationResults.summary?.initial_population || 1000} color="bg-red-500" />
                                <BarRow label="Recovered" value={currentData.R} max={simulationResults.summary?.initial_population || 1000} color="bg-blue-500" />
                                <BarRow label="Deceased" value={currentData.D} max={simulationResults.summary?.initial_population || 1000} color="bg-gray-500" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function StateCard({ label, value, color, icon }) {
    return (
        <div className="bg-gray-700 p-4 rounded-lg shadow border border-gray-600 text-center hover:shadow-lg transition-shadow">
            <div className="text-3xl mb-2">{icon}</div>
            <div className="text-2xl font-bold text-white">{value}</div>
            <div className="text-xs text-gray-300 mt-1">{label}</div>
        </div>
    )
}

function BarRow({ label, value, max, color }) {
    const percentage = (value / max) * 100

    return (
        <div>
            <div className="flex justify-between text-xs text-gray-300 mb-1">
                <span>{label}</span>
                <span>{value} ({percentage.toFixed(1)}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                    className={`${color} h-3 transition-all duration-500 rounded-full`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    )
}


function Unique3DVisualization({ currentData, currentDay, isPlaying }) {
    const total = currentData.S + currentData.E + currentData.I + currentData.R + currentData.D

    // Calculate percentages for each state
    const sPercent = (currentData.S / total) * 100
    const ePercent = (currentData.E / total) * 100
    const iPercent = (currentData.I / total) * 100
    const rPercent = (currentData.R / total) * 100
    const dPercent = (currentData.D / total) * 100

    return (
        <div className="relative bg-gray-900 rounded-2xl p-8 overflow-hidden" style={{ minHeight: '500px' }}>
            {/* Title */}
            <div className="relative z-10 text-center mb-8">
                <h3 className="text-3xl font-bold text-white mb-2">
                    3D Population Sphere - Day {currentDay}
                </h3>
                <p className="text-blue-200 text-sm">
                    {isPlaying ? '▶️ Playing' : '⏸️ Paused'} • Total Population: {total}
                </p>
            </div>

            {/* 3D Sphere Visualization */}
            <div className="relative z-10 flex items-center justify-center mb-6" style={{ height: '300px' }}>
                <div
                    className="relative transition-transform duration-1000"
                    style={{
                        width: '280px',
                        height: '280px',
                        transformStyle: 'preserve-3d',
                        transform: isPlaying ? 'rotateY(360deg)' : 'rotateY(0deg)',
                        animation: isPlaying ? 'spin3d 8s linear infinite' : 'none'
                    }}
                >
                    {/* Central 3D Sphere */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div
                            className="relative"
                            style={{
                                width: '280px',
                                height: '280px',
                                borderRadius: '50%',
                                background: `conic-gradient(
                  from 0deg,
                  #4CAF50 0deg ${sPercent * 3.6}deg,
                  #FF9800 ${sPercent * 3.6}deg ${(sPercent + ePercent) * 3.6}deg,
                  #F44336 ${(sPercent + ePercent) * 3.6}deg ${(sPercent + ePercent + iPercent) * 3.6}deg,
                  #2196F3 ${(sPercent + ePercent + iPercent) * 3.6}deg ${(sPercent + ePercent + iPercent + rPercent) * 3.6}deg,
                  #757575 ${(sPercent + ePercent + iPercent + rPercent) * 3.6}deg 360deg
                )`,
                                boxShadow: '0 0 60px rgba(147, 51, 234, 0.6), inset 0 0 60px rgba(0, 0, 0, 0.5)',
                                transform: 'rotateX(20deg)',
                                transition: 'all 0.5s ease'
                            }}
                        >
                            {/* Inner glow */}
                            <div
                                className="absolute inset-4 rounded-full"
                                style={{
                                    background: 'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3), transparent 70%)',
                                    boxShadow: 'inset 0 0 40px rgba(255, 255, 255, 0.2)'
                                }}
                            />

                            {/* Center text */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="text-center">
                                    <div className="text-white text-6xl font-bold drop-shadow-lg">
                                        {currentData.I}
                                    </div>
                                    <div className="text-red-300 text-sm font-semibold mt-1">
                                        Active Cases
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Orbiting particles representing disease spread */}
                    {currentData.I > 0 && [...Array(Math.min(currentData.I, 12))].map((_, i) => {
                        const angle = (i / Math.min(currentData.I, 12)) * 360
                        const radius = 160
                        return (
                            <div
                                key={i}
                                className="absolute w-4 h-4 bg-red-500 rounded-full shadow-lg"
                                style={{
                                    left: '50%',
                                    top: '50%',
                                    transform: `
                    translateX(-50%) translateY(-50%)
                    rotateZ(${angle}deg) translateX(${radius}px)
                    rotateZ(-${angle}deg)
                  `,
                                    opacity: 0.8,
                                    animation: `orbit 4s linear infinite`,
                                    animationDelay: `${i * 0.3}s`,
                                    boxShadow: '0 0 10px rgba(244, 67, 54, 0.8)'
                                }}
                            />
                        )
                    })}
                </div>
            </div>

            {/* 3D Floating State Cards */}
            <div className="relative z-10 grid grid-cols-5 gap-3">
                <Floating3DCard
                    label="Susceptible"
                    value={currentData.S}
                    percent={sPercent}
                    icon="🟢"
                    delay={0}
                />
                <Floating3DCard
                    label="Exposed"
                    value={currentData.E}
                    percent={ePercent}
                    icon="🟡"
                    delay={0.1}
                />
                <Floating3DCard
                    label="Infectious"
                    value={currentData.I}
                    percent={iPercent}
                    icon="🔴"
                    delay={0.2}
                />
                <Floating3DCard
                    label="Recovered"
                    value={currentData.R}
                    percent={rPercent}
                    icon="🔵"
                    delay={0.3}
                />
                <Floating3DCard
                    label="Deceased"
                    value={currentData.D}
                    percent={dPercent}
                    icon="⚫"
                    delay={0.4}
                />
            </div>

            {/* Wave effect at bottom */}
            <div className="absolute bottom-0 left-0 right-0 h-20 overflow-hidden opacity-30">
                <svg className="w-full h-full" viewBox="0 0 1200 100" preserveAspectRatio="none">
                    <path
                        d="M0,50 Q300,80 600,50 T1200,50 L1200,100 L0,100 Z"
                        fill="rgba(147, 51, 234, 0.3)"
                        className="animate-pulse"
                    />
                </svg>
            </div>

            <style jsx>{`
        @keyframes spin3d {
          from { transform: rotateY(0deg) rotateX(20deg); }
          to { transform: rotateY(360deg) rotateX(20deg); }
        }
        @keyframes orbit {
          from { transform: translateX(-50%) translateY(-50%) rotateZ(0deg) translateX(160px) rotateZ(0deg); }
          to { transform: translateX(-50%) translateY(-50%) rotateZ(360deg) translateX(160px) rotateZ(-360deg); }
        }
      `}</style>
        </div>
    )
}

function Floating3DCard({ label, value, percent, icon, delay }) {
    return (
        <div
            className="relative group cursor-pointer"
            style={{
                animation: `float 3s ease-in-out infinite`,
                animationDelay: `${delay}s`
            }}
        >
            <div
                className="bg-gray-700 p-4 rounded-xl shadow-2xl border border-gray-600 hover:border-gray-500 transition-all duration-300"
                style={{
                    transformStyle: 'preserve-3d',
                    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.4)'
                }}
            >
                <div className="text-center text-white">
                    <div className="text-3xl mb-2">{icon}</div>
                    <div className="text-2xl font-bold">{value}</div>
                    <div className="text-xs text-gray-300 mt-1">{label}</div>
                    <div className="text-xs font-semibold text-gray-300 mt-1">{percent.toFixed(1)}%</div>
                </div>
            </div>

            <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
        </div>
    )
}

function NetworkGlobeVisualization({ currentData, currentDay, isPlaying, simulationResults, currentFrame }) {
    const total = currentData.S + currentData.E + currentData.I + currentData.R + currentData.D
    const [rotation, setRotation] = useState(0)

    useEffect(() => {
        if (isPlaying) {
            const interval = setInterval(() => {
                setRotation(prev => (prev + 2) % 360)
            }, 50)
            return () => clearInterval(interval)
        }
    }, [isPlaying])

    // Generate network nodes distributed on globe surface
    const generateGlobeNodes = (count = 40) => {
        const nodes = []
        const goldenAngle = Math.PI * (3 - Math.sqrt(5))

        for (let i = 0; i < count; i++) {
            const y = 1 - (i / (count - 1)) * 2
            const radius = Math.sqrt(1 - y * y)
            const theta = goldenAngle * i

            const x = Math.cos(theta) * radius
            const z = Math.sin(theta) * radius

            // Assign state based on current simulation data
            let state = 'S'
            const rand = Math.random() * total
            if (rand < currentData.I) state = 'I'
            else if (rand < currentData.I + currentData.E) state = 'E'
            else if (rand < currentData.I + currentData.E + currentData.R) state = 'R'
            else if (rand < currentData.I + currentData.E + currentData.R + currentData.D) state = 'D'

            nodes.push({ x, y, z, state, id: i })
        }
        return nodes
    }

    const nodes = generateGlobeNodes()

    const getNodeColor = (state) => {
        const colors = {
            'S': '#4CAF50',
            'E': '#FF9800',
            'I': '#F44336',
            'R': '#2196F3',
            'D': '#757575'
        }
        return colors[state] || '#CCCCCC'
    }

    return (
        <div className="relative bg-gray-900 rounded-2xl p-8 overflow-hidden" style={{ minHeight: '500px' }}>
            {/* Title */}
            <div className="relative z-10 text-center mb-6">
                <h3 className="text-3xl font-bold text-white mb-2">
                    🌐 Network Globe - Day {currentDay}
                </h3>
                <p className="text-purple-200 text-sm">
                    {isPlaying ? '🔄 Rotating' : '⏸️ Static'} • {nodes.length} Network Nodes
                </p>
            </div>

            {/* 3D Globe Container */}
            <div className="relative z-10 flex items-center justify-center mb-6" style={{ height: '300px', perspective: '1000px' }}>
                <div
                    className="relative"
                    style={{
                        width: '280px',
                        height: '280px',
                        transformStyle: 'preserve-3d',
                        transform: `rotateY(${rotation}deg) rotateX(20deg)`,
                        transition: 'transform 0.1s linear'
                    }}
                >
                    {/* Globe sphere base */}
                    <div
                        className="absolute inset-0 rounded-full"
                        style={{
                            background: 'radial-gradient(circle at 30% 30%, rgba(100, 100, 255, 0.3), rgba(20, 20, 80, 0.8))',
                            boxShadow: '0 0 60px rgba(139, 92, 246, 0.6), inset 0 0 60px rgba(0, 0, 0, 0.5)',
                            border: '1px solid rgba(147, 51, 234, 0.3)'
                        }}
                    />

                    {/* Latitude/Longitude grid lines */}
                    {[...Array(8)].map((_, i) => (
                        <div
                            key={`lat-${i}`}
                            className="absolute left-1/2 top-1/2"
                            style={{
                                width: '280px',
                                height: '280px',
                                transform: `translate(-50%, -50%) rotateX(${i * 22.5}deg)`,
                                transformStyle: 'preserve-3d'
                            }}
                        >
                            <div
                                className="absolute inset-0 rounded-full border border-purple-400 opacity-20"
                                style={{ borderWidth: '1px' }}
                            />
                        </div>
                    ))}

                    {[...Array(12)].map((_, i) => (
                        <div
                            key={`long-${i}`}
                            className="absolute left-1/2 top-1/2"
                            style={{
                                width: '280px',
                                height: '280px',
                                transform: `translate(-50%, -50%) rotateY(${i * 15}deg)`,
                                transformStyle: 'preserve-3d'
                            }}
                        >
                            <div
                                className="absolute inset-0 rounded-full border border-purple-400 opacity-20"
                                style={{ borderWidth: '1px' }}
                            />
                        </div>
                    ))}

                    {/* Network nodes on globe surface */}
                    {nodes.map((node, idx) => {
                        const scale = 140 // Globe radius
                        const x = node.x * scale
                        const y = node.y * scale
                        const z = node.z * scale

                        // Only render nodes on visible hemisphere
                        const isVisible = z > -50

                        return isVisible && (
                            <div
                                key={node.id}
                                className="absolute"
                                style={{
                                    left: '50%',
                                    top: '50%',
                                    transform: `translate3d(${x}px, ${-y}px, ${z}px) translate(-50%, -50%)`,
                                    transformStyle: 'preserve-3d',
                                    zIndex: Math.round(z)
                                }}
                            >
                                <div
                                    className="rounded-full shadow-lg transition-all duration-500"
                                    style={{
                                        width: node.state === 'I' ? '12px' : '8px',
                                        height: node.state === 'I' ? '12px' : '8px',
                                        backgroundColor: getNodeColor(node.state),
                                        boxShadow: node.state === 'I'
                                            ? `0 0 20px ${getNodeColor(node.state)}`
                                            : `0 0 8px ${getNodeColor(node.state)}`,
                                        opacity: z > 0 ? 0.9 : 0.4,
                                        animation: node.state === 'I' ? 'pulse 1s ease-in-out infinite' : 'none'
                                    }}
                                />
                            </div>
                        )
                    })}

                    {/* Connection lines between infected nodes */}
                    {nodes.filter(n => n.state === 'I').slice(0, 5).map((node, idx) => {
                        const nextNode = nodes[(node.id + 3) % nodes.length]
                        if (nextNode.z < -50 || node.z < -50) return null

                        const scale = 140
                        const x1 = node.x * scale
                        const y1 = -node.y * scale
                        const x2 = nextNode.x * scale
                        const y2 = -nextNode.y * scale

                        const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                        const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI

                        return (
                            <div
                                key={`line-${idx}`}
                                className="absolute"
                                style={{
                                    left: '50%',
                                    top: '50%',
                                    width: `${length}px`,
                                    height: '2px',
                                    background: 'linear-gradient(to right, rgba(244, 67, 54, 0.6), rgba(244, 67, 54, 0.2))',
                                    transform: `translate(${x1}px, ${y1}px) rotate(${angle}deg)`,
                                    transformOrigin: '0 0',
                                    transformStyle: 'preserve-3d',
                                    animation: 'pulse 2s ease-in-out infinite',
                                    zIndex: Math.round((node.z + nextNode.z) / 2)
                                }}
                            />
                        )
                    })}

                    {/* Center info */}
                    <div className="absolute inset-0 flex items-center justify-center" style={{ transform: 'translateZ(50px)' }}>
                        <div className="text-center bg-black bg-opacity-50 px-4 py-2 rounded-lg backdrop-blur-sm">
                            <div className="text-white text-3xl font-bold drop-shadow-lg">
                                {currentData.I}
                            </div>
                            <div className="text-red-300 text-xs font-semibold">
                                Infected
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* State Cards */}
            <div className="relative z-10 grid grid-cols-5 gap-3">
                <Floating3DCard
                    label="Susceptible"
                    value={currentData.S}
                    percent={(currentData.S / total) * 100}
                    icon="🟢"
                    delay={0}
                />
                <Floating3DCard
                    label="Exposed"
                    value={currentData.E}
                    percent={(currentData.E / total) * 100}
                    icon="🟡"
                    delay={0.1}
                />
                <Floating3DCard
                    label="Infectious"
                    value={currentData.I}
                    percent={(currentData.I / total) * 100}
                    icon="🔴"
                    delay={0.2}
                />
                <Floating3DCard
                    label="Recovered"
                    value={currentData.R}
                    percent={(currentData.R / total) * 100}
                    icon="🔵"
                    delay={0.3}
                />
                <Floating3DCard
                    label="Deceased"
                    value={currentData.D}
                    percent={(currentData.D / total) * 100}
                    icon="⚫"
                    delay={0.4}
                />
            </div>

            <style jsx>{`
        @keyframes twinkle {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.5); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 1; }
        }
      `}</style>
        </div>
    )
}

function LegendItem({ color, label, count }) {
    return (
        <div className="flex items-center gap-2 bg-white bg-opacity-10 px-3 py-1 rounded-full backdrop-blur-sm">
            <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: color, boxShadow: `0 0 6px ${color}` }}
            />
            <span className="text-white text-xs font-medium">{label}: {count}</span>
        </div>
    )
}
