// components/Network3D.jsx - 3D Network Visualization with Disease Spread Animation
import { useRef, useState, useEffect, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Line, Text } from '@react-three/drei'
import * as THREE from 'three'

// Node component - represents a person in the network
function Node({ position, state, size = 0.5 }) {
    const meshRef = useRef()

    // Color mapping based on disease state
    const colorMap = {
        'S': '#4CAF50',  // Susceptible - Green
        'E': '#FF9800',  // Exposed - Orange
        'I': '#F44336',  // Infected - Red
        'R': '#2196F3',  // Recovered - Blue
        'D': '#757575',  // Deceased - Gray
        'V': '#9C27B0'   // Vaccinated - Purple
    }

    const color = colorMap[state] || '#FFFFFF'

    // Pulsing animation for infected nodes, make deceased nodes fade
    useFrame((frameState) => {
        if (meshRef.current) {
            if (state === 'I') {
                const scale = 1 + Math.sin(frameState.clock.elapsedTime * 3) * 0.2
                meshRef.current.scale.setScalar(scale)
            } else if (state === 'D') {
                // Deceased nodes are smaller and dimmer
                meshRef.current.scale.setScalar(0.6)
            }
        }
    })

    return (
        <mesh ref={meshRef} position={position}>
            <sphereGeometry args={[size, 16, 16]} />
            <meshStandardMaterial
                color={color}
                emissive={state === 'I' ? '#FF0000' : state === 'D' ? '#000000' : '#000000'}
                emissiveIntensity={state === 'I' ? 0.5 : 0}
                opacity={state === 'D' ? 0.6 : 1.0}
                transparent={state === 'D'}
            />
        </mesh>
    )
}

// Edge component - connection between nodes
function Edge({ start, end, opacity = 0.3 }) {
    const points = useMemo(() => [
        new THREE.Vector3(...start),
        new THREE.Vector3(...end)
    ], [start, end])

    return (
        <Line
            points={points}
            color="#888888"
            lineWidth={1}
            opacity={opacity}
            transparent
        />
    )
}

// Main 3D Network Scene
function NetworkScene({ nodes, edges, currentDay }) {
    return (
        <>
            {/* Lighting */}
            <ambientLight intensity={0.6} />
            <pointLight position={[10, 10, 10]} intensity={0.8} />
            <pointLight position={[-10, -10, -10]} intensity={0.4} />

            {/* Draw edges first (behind nodes) */}
            {edges.map((edge, i) => (
                <Edge
                    key={`edge-${i}`}
                    start={edge.start}
                    end={edge.end}
                    opacity={0.2}
                />
            ))}

            {/* Draw nodes */}
            {nodes.map((node, i) => (
                <Node
                    key={`node-${i}`}
                    position={node.position}
                    state={node.states[currentDay] || 'S'}
                    size={0.3}
                />
            ))}
        </>
    )
}

// Main Network3D Component
export default function Network3D({ simulationData }) {
    const [currentDay, setCurrentDay] = useState(0)
    const [isPlaying, setIsPlaying] = useState(false)
    const [speed, setSpeed] = useState(100) // ms per day

    // Generate 3D layout from simulation data
    const { nodes, edges, maxDay } = useMemo(() => {
        if (!simulationData || !simulationData.history) {
            // Generate sample data for demonstration
            return generateSampleNetwork()
        }

        // Parse actual simulation data
        // This would require backend to provide network structure
        // For now, generate based on population size
        const population = simulationData.history.S[0]
        return generateNetworkFromSimulation(simulationData, population)
    }, [simulationData])

    // Animation loop
    useEffect(() => {
        if (!isPlaying || currentDay >= maxDay) return

        const timer = setTimeout(() => {
            setCurrentDay(d => (d + 1) % (maxDay + 1))
        }, speed)

        return () => clearTimeout(timer)
    }, [isPlaying, currentDay, maxDay, speed])

    // Calculate statistics for current day
    const stats = useMemo(() => {
        const counts = { S: 0, E: 0, I: 0, R: 0, D: 0, V: 0 }
        nodes.forEach(node => {
            const state = node.states[currentDay] || 'S'
            counts[state]++
        })
        return counts
    }, [nodes, currentDay])

    return (
        <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h3 className="text-2xl font-bold mb-4 text-white">🌐 3D Network Simulation</h3>

            {/* 3D Canvas */}
            <div className="w-full h-150 bg-gray-900 rounded-lg overflow-hidden relative">
                <Canvas>
                    <PerspectiveCamera makeDefault position={[0, 0, 50]} />
                    <OrbitControls
                        enableDamping
                        dampingFactor={0.05}
                        minDistance={20}
                        maxDistance={100}
                    />
                    <NetworkScene nodes={nodes} edges={edges} currentDay={currentDay} />
                </Canvas>

                {/* Day counter overlay */}
                <div className="absolute top-4 left-4 bg-black bg-opacity-70 text-white px-4 py-2 rounded">
                    <div className="text-2xl font-bold">Day {currentDay}</div>
                </div>

                {/* Statistics overlay */}
                <div className="absolute top-4 right-4 bg-black bg-opacity-70 text-white px-4 py-2 rounded text-sm">
                    <div className="font-bold mb-2">Population Status</div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-green-500"></div>
                        <span>Susceptible: {stats.S}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                        <span>Exposed: {stats.E}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                        <span>Infected: {stats.I}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                        <span>Recovered: {stats.R}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-gray-500"></div>
                        <span className="font-semibold">Deceased: {stats.D}</span>
                    </div>
                    {stats.V > 0 && (
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                            <span>Vaccinated: {stats.V}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Controls */}
            <div className="mt-4 space-y-4">
                {/* Timeline slider */}
                <div className="flex items-center gap-4">
                    <label className="font-semibold text-gray-300">Timeline:</label>
                    <input
                        type="range"
                        min="0"
                        max={maxDay}
                        value={currentDay}
                        onChange={(e) => setCurrentDay(parseInt(e.target.value))}
                        className="flex-1"
                    />
                    <span className="text-gray-300">{currentDay} / {maxDay}</span>
                </div>

                {/* Playback controls */}
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                        {isPlaying ? '⏸️ Pause' : '▶️ Play'}
                    </button>
                    <button
                        onClick={() => setCurrentDay(0)}
                        className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
                    >
                        ⏮️ Reset
                    </button>

                    {/* Speed control */}
                    <div className="flex items-center gap-2">
                        <label className="font-semibold text-gray-300">Speed:</label>
                        <select
                            value={speed}
                            onChange={(e) => setSpeed(parseInt(e.target.value))}
                            className="px-3 py-2 border border-gray-300 rounded-lg"
                        >
                            <option value="500">0.5x</option>
                            <option value="200">1x</option>
                            <option value="100">2x</option>
                            <option value="50">4x</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Legend */}
            <div className="mt-4 p-4 bg-gray-700 rounded-lg">
                <div className="font-semibold mb-2">🎨 Color Legend:</div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-green-500"></div>
                        <span>Susceptible (Healthy)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-orange-500"></div>
                        <span>Exposed (Incubating)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-red-500 animate-pulse"></div>
                        <span>Infected (Contagious)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-blue-500"></div>
                        <span>Recovered (Immune)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-gray-500"></div>
                        <span>Deceased</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-purple-500"></div>
                        <span>Vaccinated</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

// Generate sample network for demonstration
function generateSampleNetwork() {
    const numNodes = 100
    const nodes = []
    const edges = []

    // Create nodes in 3D space using force-directed layout approximation
    for (let i = 0; i < numNodes; i++) {
        // Distribute nodes in a sphere
        const phi = Math.acos(2 * Math.random() - 1)
        const theta = 2 * Math.PI * Math.random()
        const radius = 20

        const x = radius * Math.sin(phi) * Math.cos(theta)
        const y = radius * Math.sin(phi) * Math.sin(theta)
        const z = radius * Math.cos(phi)

        // Generate state progression over time
        const states = []
        let currentState = 'S'

        // Initial infection for a few nodes
        if (i < 5) {
            currentState = 'I'
        }

        for (let day = 0; day < 150; day++) {
            // Simple state transition logic
            if (currentState === 'I' && day > i + 20) {
                currentState = Math.random() < 0.95 ? 'R' : 'D'
            } else if (currentState === 'S' && Math.random() < 0.02 * day / 150) {
                currentState = 'I'
            }
            states.push(currentState)
        }

        nodes.push({ position: [x, y, z], states })
    }

    // Create edges (scale-free network)
    const avgDegree = 4
    for (let i = 0; i < numNodes; i++) {
        const numConnections = Math.floor(avgDegree + Math.random() * 3)
        for (let j = 0; j < numConnections; j++) {
            // Preferential attachment - connect to nodes with more connections
            let target = Math.floor(Math.random() * numNodes)
            while (target === i) {
                target = Math.floor(Math.random() * numNodes)
            }

            edges.push({
                start: nodes[i].position,
                end: nodes[target].position
            })
        }
    }

    return { nodes, edges, maxDay: 149 }
}

// Generate network from actual simulation data
function generateNetworkFromSimulation(simulationData, population) {
    // Simplified version - would need backend support for full implementation
    const numNodes = Math.min(population, 200) // Limit for performance
    const maxDay = simulationData.history.S.length - 1

    const nodes = []
    const edges = []

    // Create nodes
    for (let i = 0; i < numNodes; i++) {
        const phi = Math.acos(2 * Math.random() - 1)
        const theta = 2 * Math.PI * Math.random()
        const radius = 20

        const x = radius * Math.sin(phi) * Math.cos(theta)
        const y = radius * Math.sin(phi) * Math.sin(theta)
        const z = radius * Math.cos(phi)

        // Estimate states based on population proportions
        const states = []
        for (let day = 0; day <= maxDay; day++) {
            const totalPop = simulationData.history.S[0]
            const iRatio = simulationData.history.I[day] / totalPop
            const rRatio = simulationData.history.R[day] / totalPop

            const rand = Math.random()
            let state = 'S'
            if (rand < iRatio) state = 'I'
            else if (rand < iRatio + rRatio) state = 'R'

            states.push(state)
        }

        nodes.push({ position: [x, y, z], states })
    }

    // Create edges
    for (let i = 0; i < numNodes; i++) {
        const numConnections = 3 + Math.floor(Math.random() * 4)
        for (let j = 0; j < numConnections; j++) {
            const target = Math.floor(Math.random() * numNodes)
            if (target !== i) {
                edges.push({
                    start: nodes[i].position,
                    end: nodes[target].position
                })
            }
        }
    }

    return { nodes, edges, maxDay }
}
