// components/LoadingSpinner.jsx
export default function LoadingSpinner({ message = 'Loading...' }) {
    return (
        <div className="bg-gray-800 rounded-2xl shadow-2xl p-16 text-center border border-gray-700">
            <div className="flex flex-col items-center justify-center space-y-6">
                <div className="relative w-24 h-24">
                    {/* Outer ring */}
                    <div className="absolute inset-0 border-8 border-purple-200 rounded-full"></div>
                    {/* Spinning gradient ring */}
                    <div className="absolute inset-0 border-8 border-transparent rounded-full border-t-purple-600 border-r-pink-600 animate-spin"></div>
                    {/* Center icon */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-4xl">🦠</span>
                    </div>
                </div>
                <div className="space-y-2">
                    <p className="text-white text-xl font-bold">{message}</p>
                    <div className="flex justify-center gap-2">
                        <div className="w-3 h-3 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                        <div className="w-3 h-3 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-3 h-3 bg-pink-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                </div>
            </div>
        </div>
    )
}
