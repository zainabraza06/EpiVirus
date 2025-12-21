// components/AdvancedNetworkConfig.jsx
import { useState } from 'react'

export default function AdvancedNetworkConfig({ networkType, onParamsChange, initialParams = {} }) {
    const [params, setParams] = useState(initialParams)

    const handleChange = (key, value) => {
        const newParams = { ...params, [key]: value }
        setParams(newParams)
        onParamsChange(newParams)
    }

    const renderErdosRenyi = () => (
        <div className="space-y-6">
            <div className="bg-gray-700 p-5 rounded-xl shadow-sm border border-gray-600">
                <label className="block text-sm font-bold text-gray-200 mb-3 flex items-center justify-between">
                    <span>Connection Probability (p)</span>
                    <span className="text-lg text-indigo-600">{(params.erdos_p || 0.01).toFixed(3)}</span>
                </label>
                <input
                    type="range"
                    min="0.001"
                    max="0.1"
                    step="0.001"
                    value={params.erdos_p || 0.01}
                    onChange={(e) => handleChange('erdos_p', parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <p className="text-xs text-gray-400 mt-2 italic">
                    📊 Probability that any two nodes are connected
                </p>
            </div>
        </div>
    )

    const renderWattsStrogatz = () => (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-700 p-5 rounded-xl shadow-sm border border-gray-600">
                <label className="block text-sm font-bold text-gray-200 mb-3 flex items-center justify-between">
                    <span>K Neighbors</span>
                    <span className="text-lg text-purple-600">{params.watts_k || 8}</span>
                </label>
                <input
                    type="range"
                    min="2"
                    max="20"
                    step="1"
                    value={params.watts_k || 8}
                    onChange={(e) => handleChange('watts_k', parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                />
                <p className="text-xs text-gray-400 mt-2 italic">
                    🔗 Number of nearest neighbors in ring topology
                </p>
            </div>

            <div className="bg-gray-700 p-5 rounded-xl shadow-sm border border-gray-600">
                <label className="block text-sm font-bold text-gray-200 mb-3 flex items-center justify-between">
                    <span>Rewiring Probability (p)</span>
                    <span className="text-lg text-purple-600">{(params.watts_p || 0.3).toFixed(2)}</span>
                </label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={params.watts_p || 0.3}
                    onChange={(e) => handleChange('watts_p', parseFloat(e.target.value))}
                    className="w-full accent-indigo-500"
                />
                <p className="text-xs text-gray-400 mt-1">
                    Probability of rewiring each edge (creates small-world effect)
                </p>
            </div>
        </div>
    )

    const renderBarabasiAlbert = () => (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-200 mb-2">
                    Attachment Parameter (m): {params.barabasi_m || 3}
                </label>
                <input
                    type="range"
                    min="1"
                    max="10"
                    step="1"
                    value={params.barabasi_m || 3}
                    onChange={(e) => handleChange('barabasi_m', parseInt(e.target.value))}
                    className="w-full"
                />
                <p className="text-xs text-gray-400 mt-1">
                    Number of edges to attach from new node (creates scale-free network)
                </p>
            </div>
        </div>
    )

    const renderStochasticBlock = () => (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-700 p-4 rounded-xl shadow-sm border border-gray-600">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                    Number of Blocks: <span className="text-indigo-400 font-semibold">{params.n_blocks || 5}</span>
                </label>
                <input
                    type="range"
                    min="2"
                    max="20"
                    step="1"
                    value={params.n_blocks || 5}
                    onChange={(e) => handleChange('n_blocks', parseInt(e.target.value))}
                    className="w-full accent-indigo-500"
                />
                <p className="text-xs text-gray-400 mt-1">
                    Number of communities/blocks in the network
                </p>
            </div>

            <div className="bg-gray-700 p-4 rounded-xl shadow-sm border border-gray-600">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                    Intra-Block Probability: <span className="text-gray-200 font-semibold">{(params.block_intra || 0.15).toFixed(3)}</span>
                </label>
                <input
                    type="range"
                    min="0.01"
                    max="0.5"
                    step="0.01"
                    value={params.block_intra || 0.15}
                    onChange={(e) => handleChange('block_intra', parseFloat(e.target.value))}
                    className="w-full accent-indigo-500"
                />
                <p className="text-xs text-gray-400 mt-1">
                    Connection probability within same block
                </p>
            </div>

            <div className="bg-gray-700 p-4 rounded-xl shadow-sm border border-gray-600">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                    Inter-Block Probability: <span className="text-gray-200 font-semibold">{(params.block_inter || 0.01).toFixed(3)}</span>
                </label>
                <input
                    type="range"
                    min="0.001"
                    max="0.1"
                    step="0.001"
                    value={params.block_inter || 0.01}
                    onChange={(e) => handleChange('block_inter', parseFloat(e.target.value))}
                    className="w-full accent-indigo-500"
                />
                <p className="text-xs text-gray-400 mt-1">
                    Connection probability between different blocks
                </p>
            </div>
        </div>
    )

    const renderHybridMultilayer = () => (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <h4 className="font-semibold text-white mb-3">🏠 Household Layer</h4>
                <div className="space-y-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                            Avg Household Size: <span className="text-gray-200 font-semibold">{params.household_size || 3}</span>
                        </label>
                        <input
                            type="range"
                            min="1"
                            max="8"
                            step="1"
                            value={params.household_size || 3}
                            onChange={(e) => handleChange('household_size', parseInt(e.target.value))}
                            className="w-full accent-indigo-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                            Connection Probability: <span className="text-gray-200 font-semibold">{(params.household_p || 0.9).toFixed(2)}</span>
                        </label>
                        <input
                            type="range"
                            min="0.5"
                            max="1"
                            step="0.01"
                            value={params.household_p || 0.9}
                            onChange={(e) => handleChange('household_p', parseFloat(e.target.value))}
                            className="w-full accent-indigo-500"
                        />
                    </div>
                </div>
            </div>

            <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <h4 className="font-semibold text-white mb-3">🏢 Workplace Layer</h4>
                <div className="space-y-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                            Avg Workplace Size: <span className="text-gray-200 font-semibold">{params.workplace_size || 20}</span>
                        </label>
                        <input
                            type="range"
                            min="5"
                            max="100"
                            step="5"
                            value={params.workplace_size || 20}
                            onChange={(e) => handleChange('workplace_size', parseInt(e.target.value))}
                            className="w-full accent-indigo-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                            Connection Probability: <span className="text-gray-200 font-semibold">{(params.workplace_p || 0.3).toFixed(2)}</span>
                        </label>
                        <input
                            type="range"
                            min="0.1"
                            max="0.8"
                            step="0.01"
                            value={params.workplace_p || 0.3}
                            onChange={(e) => handleChange('workplace_p', parseFloat(e.target.value))}
                            className="w-full accent-indigo-500"
                        />
                    </div>
                </div>
            </div>

            <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <h4 className="font-semibold text-white mb-3">🎓 School Layer</h4>
                <div className="space-y-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                            Avg School Size: <span className="text-gray-200 font-semibold">{params.school_size || 30}</span>
                        </label>
                        <input
                            type="range"
                            min="10"
                            max="100"
                            step="5"
                            value={params.school_size || 30}
                            onChange={(e) => handleChange('school_size', parseInt(e.target.value))}
                            className="w-full accent-indigo-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                            Connection Probability: <span className="text-gray-200 font-semibold">{(params.school_p || 0.4).toFixed(2)}</span>
                        </label>
                        <input
                            type="range"
                            min="0.1"
                            max="0.8"
                            step="0.01"
                            value={params.school_p || 0.4}
                            onChange={(e) => handleChange('school_p', parseFloat(e.target.value))}
                            className="w-full accent-indigo-500"
                        />
                    </div>
                </div>
            </div>

            <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <h4 className="font-semibold text-white mb-3">🌐 Community Layer</h4>
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                        Random Connection Probability: <span className="text-gray-200 font-semibold">{(params.community_p || 0.05).toFixed(3)}</span>
                    </label>
                    <input
                        type="range"
                        min="0.001"
                        max="0.2"
                        step="0.001"
                        value={params.community_p || 0.05}
                        onChange={(e) => handleChange('community_p', parseFloat(e.target.value))}
                        className="w-full accent-indigo-500"
                    />
                    <p className="text-xs text-gray-400 mt-1">
                        Random connections between individuals (friends, acquaintances)
                    </p>
                </div>
            </div>
        </div>
    )

    return (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span>⚙️</span>
                <span>Advanced Network Parameters</span>
            </h3>

            {networkType === 'erdos_renyi' && renderErdosRenyi()}
            {networkType === 'watts_strogatz' && renderWattsStrogatz()}
            {networkType === 'barabasi_albert' && renderBarabasiAlbert()}
            {networkType === 'stochastic_block' && renderStochasticBlock()}
            {networkType === 'hybrid_multilayer' && renderHybridMultilayer()}
            {networkType === 'hybrid' && renderHybridMultilayer()}
        </div>
    )
}
