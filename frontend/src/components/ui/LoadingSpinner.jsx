// components/ui/LoadingSpinner.jsx
export default function LoadingSpinner({ message = 'Loading…' }) {
    return (
        <div className="flex items-center gap-4 text-gray-300" role="status">
            <div className="relative w-10 h-10 shrink-0">
                <div className="absolute inset-0 border-4 border-gray-700 rounded-full" />
                <div className="absolute inset-0 border-4 border-transparent border-t-indigo-500 rounded-full animate-spin" />
            </div>
            <span className="text-sm">{message}</span>
        </div>
    )
}
