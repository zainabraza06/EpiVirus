// components/Header.jsx
export default function Header() {
    return (
        <header className="bg-gray-900 shadow-2xl border-b border-gray-800">
            <div className="container mx-auto px-4 py-6 max-w-7xl">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="text-5xl">🦠</div>
                        <div>
                            <h1 className="text-3xl font-bold text-white">EpiVirus</h1>
                            <p className="text-gray-300 text-sm">Pandemic Simulation Platform</p>
                        </div>
                    </div>
                    <div className="hidden md:flex items-center space-x-6 text-gray-300">
                        <a href="#simulation" className="hover:text-white transition-colors">Simulation</a>
                        <a href="#results" className="hover:text-white transition-colors">Results</a>
                        <a href="#docs" className="hover:text-white transition-colors">Docs</a>
                    </div>
                </div>
            </div>
        </header>
    )
}
