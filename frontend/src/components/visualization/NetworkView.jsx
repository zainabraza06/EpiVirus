// components/visualization/NetworkView.jsx
//
// 3D contact network with day-by-day playback. Node positions, edges and each
// node's state timeline all come from the backend's /network endpoint. The
// previous version invented positions and re-rolled every node's state each day
// from the population-level proportions, so individuals flickered between
// recovered and susceptible at random.
import { useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'
import * as THREE from 'three'

import { apiUrl } from '../../api'
import { STATE_COLORS, STATE_LABELS, STATE_ORDER } from '../charts/chartTokens'

// One instanced mesh per state, re-coloured per frame. Drawing a separate
// <mesh> per node made the scene unusable past a couple of hundred people.
function NodeCloud({ nodes, states }) {
    const meshRef = useRef()
    const pulseRef = useRef(0)

    const { positions, colorArray } = useMemo(() => {
        const positions = new Float32Array(nodes.length * 3)
        nodes.forEach((node, i) => {
            positions[i * 3] = node.x
            positions[i * 3 + 1] = node.y
            positions[i * 3 + 2] = node.z
        })
        return { positions, colorArray: new Float32Array(nodes.length * 3) }
    }, [nodes])

    // Re-apply the colours and per-node scale whenever the day changes
    useEffect(() => {
        const mesh = meshRef.current
        if (!mesh || !states) return

        const dummy = new THREE.Object3D()
        const color = new THREE.Color()

        for (let i = 0; i < nodes.length; i++) {
            const state = states[i] || 'S'
            color.set(STATE_COLORS[state] || '#9ca3af')
            color.toArray(colorArray, i * 3)

            // Deceased shrink away; active infections stand out
            const scale = state === 'D' ? 0.45 : state === 'I' ? 1.25 : 0.85
            dummy.position.set(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2])
            dummy.scale.setScalar(scale)
            dummy.updateMatrix()
            mesh.setMatrixAt(i, dummy.matrix)
        }

        mesh.instanceMatrix.needsUpdate = true
        if (mesh.geometry.attributes.color) {
            mesh.geometry.attributes.color.needsUpdate = true
        }
    }, [states, nodes, positions, colorArray])

    // Gentle breathing so a live epidemic reads as alive
    useFrame((_, delta) => {
        pulseRef.current += delta
        if (meshRef.current) {
            meshRef.current.material.emissiveIntensity =
                0.25 + Math.sin(pulseRef.current * 2) * 0.1
        }
    })

    return (
        <instancedMesh ref={meshRef} args={[undefined, undefined, nodes.length]}>
            <sphereGeometry args={[0.42, 12, 12]}>
                <instancedBufferAttribute attach="attributes-color" args={[colorArray, 3]} />
            </sphereGeometry>
            <meshStandardMaterial vertexColors emissive="#ffffff" emissiveIntensity={0.25} />
        </instancedMesh>
    )
}

function EdgeLines({ nodes, edges }) {
    const geometry = useMemo(() => {
        const points = new Float32Array(edges.length * 6)
        edges.forEach(([a, b], i) => {
            const from = nodes[a]
            const to = nodes[b]
            if (!from || !to) return
            points.set([from.x, from.y, from.z, to.x, to.y, to.z], i * 6)
        })
        const geo = new THREE.BufferGeometry()
        geo.setAttribute('position', new THREE.BufferAttribute(points, 3))
        return geo
    }, [nodes, edges])

    useEffect(() => () => geometry.dispose(), [geometry])

    return (
        <lineSegments geometry={geometry}>
            <lineBasicMaterial color="#4b5563" transparent opacity={0.28} />
        </lineSegments>
    )
}

export default function NetworkView({ simulationId, history }) {
    // One piece of state tagged with the simulation it belongs to, so the
    // loading condition is derived rather than set synchronously in an effect.
    const [loaded, setLoaded] = useState(null)
    const [frame, setFrame] = useState(0)
    const [isPlaying, setIsPlaying] = useState(false)
    const [fps, setFps] = useState(5)

    useEffect(() => {
        if (!simulationId) return

        let cancelled = false

        fetch(apiUrl(`/api/simulation/${simulationId}/network`))
            .then((response) => {
                if (!response.ok) throw new Error(`Network data unavailable (${response.status})`)
                return response.json()
            })
            .then((data) => {
                if (cancelled) return
                setLoaded({ id: simulationId, network: data, error: null })
                setFrame(0)
                setIsPlaying(false)
            })
            .catch((err) => {
                if (cancelled) return
                setLoaded({ id: simulationId, network: null, error: err.message })
            })

        return () => {
            cancelled = true
        }
    }, [simulationId])

    const isCurrent = loaded?.id === simulationId
    const network = isCurrent ? loaded.network : null
    const error = isCurrent ? loaded.error : null
    const loading = Boolean(simulationId) && !isCurrent

    const frameCount = network?.frames?.length ?? 0

    // Playback
    useEffect(() => {
        if (!isPlaying || frameCount === 0) return
        const timer = setInterval(() => {
            setFrame((current) => {
                if (current >= frameCount - 1) {
                    setIsPlaying(false)
                    return current
                }
                return current + 1
            })
        }, 1000 / fps)
        return () => clearInterval(timer)
    }, [isPlaying, fps, frameCount])

    const states = useMemo(() => {
        if (!network?.frames?.[frame]) return null
        return network.frames[frame].split('')
    }, [network, frame])

    const counts = useMemo(() => {
        const tally = Object.fromEntries(STATE_ORDER.map((s) => [s, 0]))
        states?.forEach((state) => {
            if (tally[state] !== undefined) tally[state] += 1
        })
        return tally
    }, [states])

    const day = network?.frame_days?.[frame] ?? 0

    if (loading) {
        return (
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-12 text-center text-gray-400">
                Loading network structure…
            </div>
        )
    }

    if (error || !network) {
        return (
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-12 text-center text-gray-400">
                {error || 'Run a simulation to explore its contact network.'}
            </div>
        )
    }

    // Population-level counts for the sampled view are scaled from the real
    // history so the numbers on screen are the simulation's, not the sample's.
    const totalPopulation = history?.S?.[0] !== undefined
        ? network.total_nodes
        : network.nodes.length

    return (
        <div className="space-y-4">
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 shadow-lg">
                <div className="flex flex-wrap items-baseline justify-between gap-2 mb-4">
                    <div>
                        <h3 className="text-lg font-semibold text-gray-50">Contact network</h3>
                        <p className="text-sm text-gray-400">
                            {network.sampled
                                ? `${network.nodes.length} of ${totalPopulation.toLocaleString()} people shown, sampled to keep playback smooth`
                                : `All ${network.nodes.length.toLocaleString()} people, ${network.total_edges.toLocaleString()} contacts`}
                        </p>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold text-gray-50 tabular-nums">Day {day}</div>
                        <div className="text-xs text-gray-400">
                            frame {frame + 1} of {frameCount}
                        </div>
                    </div>
                </div>

                <div className="w-full bg-gray-900 rounded-lg overflow-hidden border border-gray-700"
                     style={{ height: 520 }}>
                    <Canvas dpr={[1, 2]}>
                        <PerspectiveCamera makeDefault position={[0, 0, 55]} />
                        <OrbitControls
                            enableDamping
                            dampingFactor={0.08}
                            minDistance={15}
                            maxDistance={140}
                        />
                        <ambientLight intensity={0.75} />
                        <pointLight position={[30, 30, 30]} intensity={120} decay={2} />
                        <pointLight position={[-30, -20, -20]} intensity={60} decay={2} />
                        <EdgeLines nodes={network.nodes} edges={network.edges} />
                        <NodeCloud nodes={network.nodes} states={states} />
                    </Canvas>
                </div>

                {/* Legend - identity is never colour alone, every swatch is labelled */}
                <div className="flex flex-wrap gap-x-5 gap-y-2 mt-4">
                    {STATE_ORDER.map((state) => (
                        <div key={state} className="flex items-center gap-2">
                            <span
                                className="w-3 h-3 rounded-full shrink-0"
                                style={{ backgroundColor: STATE_COLORS[state] }}
                            />
                            <span className="text-sm text-gray-300">{STATE_LABELS[state]}</span>
                            <span className="text-sm font-semibold text-gray-50 tabular-nums">
                                {counts[state]}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Playback controls */}
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 shadow-lg space-y-4">
                <input
                    type="range"
                    min="0"
                    max={Math.max(0, frameCount - 1)}
                    value={frame}
                    onChange={(event) => {
                        setIsPlaying(false)
                        setFrame(parseInt(event.target.value, 10))
                    }}
                    className="w-full accent-indigo-500"
                    aria-label="Simulation day"
                />

                <div className="flex flex-wrap items-center gap-3">
                    <button
                        type="button"
                        onClick={() => {
                            if (frame >= frameCount - 1) setFrame(0)
                            setIsPlaying(!isPlaying)
                        }}
                        className="px-5 py-2 rounded-lg font-semibold text-white bg-indigo-600 hover:bg-indigo-500 transition-colors"
                    >
                        {isPlaying ? 'Pause' : 'Play'}
                    </button>
                    <button
                        type="button"
                        onClick={() => {
                            setIsPlaying(false)
                            setFrame(0)
                        }}
                        className="px-5 py-2 rounded-lg font-semibold text-gray-200 bg-gray-700 hover:bg-gray-600 transition-colors"
                    >
                        Reset
                    </button>

                    <div className="flex items-center gap-2 ml-auto">
                        <span className="text-sm text-gray-400">Speed</span>
                        {[1, 2, 5, 10, 20].map((option) => (
                            <button
                                key={option}
                                type="button"
                                onClick={() => setFps(option)}
                                className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
                                    fps === option
                                        ? 'bg-indigo-600 text-white'
                                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                }`}
                            >
                                {option}×
                            </button>
                        ))}
                    </div>
                </div>

                <p className="text-xs text-gray-400">
                    Drag to rotate, scroll to zoom. Each sphere is one person and each line a
                    contact along which the disease can spread.
                </p>
            </div>
        </div>
    )
}
