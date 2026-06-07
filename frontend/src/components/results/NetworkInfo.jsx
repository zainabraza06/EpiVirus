// components/NetworkInfo.jsx
export default function NetworkInfo({ info }) {
    return (
        <div className="bg-linear-to-br from-gray-800 to-gray-900 rounded-2xl p-6 border-2 border-gray-700 shadow-xl">
            <div className="flex items-center gap-2 mb-6">
                <span className="text-2xl">🌐</span>
                <h4 className="text-xl font-bold text-white">Network Information</h4>
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded-xl px-5 py-4 shadow-md hover:shadow-lg transition-shadow border border-gray-600">
                    <div className="text-sm text-gray-300 font-semibold mb-1 flex items-center gap-1">
                        <span>🔵</span>
                        <span>Nodes</span>
                    </div>
                    <div className="text-3xl font-bold text-white">{info.nodes.toLocaleString()}</div>
                </div>
                <div className="bg-gray-700 rounded-xl px-5 py-4 shadow-md hover:shadow-lg transition-shadow border border-gray-600">
                    <div className="text-sm text-gray-300 font-semibold mb-1 flex items-center gap-1">
                        <span>🔗</span>
                        <span>Edges</span>
                    </div>
                    <div className="text-3xl font-bold text-white">{info.edges.toLocaleString()}</div>
                </div>
                <div className="bg-gray-700 rounded-xl px-5 py-4 col-span-2 shadow-md hover:shadow-lg transition-shadow border border-gray-600">
                    <div className="text-sm text-gray-300 font-semibold mb-1 flex items-center gap-1">
                        <span>📊</span>
                        <span>Average Degree</span>
                    </div>
                    <div className="text-3xl font-bold text-white">{info.avg_degree.toFixed(2)}</div>
                </div>
            </div>
        </div>
    )
}
