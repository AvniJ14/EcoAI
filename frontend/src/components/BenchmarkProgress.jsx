
function BenchmarkProgress({ progress }) {

    if (!progress) {
        return null;
    }

    const percentage = Math.min(
        100,
        Math.max(0, Number(progress.progress_percent) || 0)
    );

    const status = progress.status || "idle";

    const statusStyles = {
        idle: "bg-gray-100 text-gray-600",
        queued: "bg-yellow-100 text-yellow-700",
        running: "bg-blue-100 text-blue-700",
        completed: "bg-emerald-100 text-emerald-700",
        failed: "bg-red-100 text-red-700"
    };

    const statusLabel = {
        idle: "Idle",
        queued: "Queued",
        running: "Running",
        completed: "Completed",
        failed: "Failed"
    };

    return (
        <section className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">

            {/* Header */}

            <div className="flex flex-wrap justify-between items-center gap-3 mb-6">

                <div>
                    <h2 className="text-lg font-bold text-gray-900">
                        Benchmark Execution
                    </h2>

                    <p className="text-sm text-gray-500 mt-1">
                        Live machine learning evaluation progress
                    </p>
                </div>

                <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        statusStyles[status] || statusStyles.idle
                    }`}
                >
                    {statusLabel[status] || status}
                </span>

            </div>

            {/* Progress percentage */}

            <div className="mb-6">

                <div className="flex justify-between items-end mb-2">

                    <span className="text-sm font-medium text-gray-600">
                        Overall Progress
                    </span>

                    <span className="text-2xl font-bold text-emerald-700">
                        {percentage.toFixed(1)}%
                    </span>

                </div>

                <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">

                    <div
                        className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                    />

                </div>

            </div>

            {/* Experiment statistics */}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">

                <div className="bg-gray-50 rounded-xl p-4">
                    <p className="text-xs text-gray-500">
                        Completed Experiments
                    </p>

                    <p className="text-xl font-bold text-gray-900 mt-1">
                        {progress.completed_experiments ?? 0}
                        <span className="text-sm font-medium text-gray-400">
                            {" "}/ {progress.total_experiments ?? 30}
                        </span>
                    </p>
                </div>

                <div className="bg-gray-50 rounded-xl p-4">
                    <p className="text-xs text-gray-500">
                        Completed Models
                    </p>

                    <p className="text-xl font-bold text-gray-900 mt-1">
                        {progress.completed_models ?? 0}
                        <span className="text-sm font-medium text-gray-400">
                            {" "}/ {progress.total_models ?? 6}
                        </span>
                    </p>
                </div>

                <div className="bg-gray-50 rounded-xl p-4">
                    <p className="text-xs text-gray-500">
                        Current Model
                    </p>

                    <p className="text-sm font-bold text-gray-900 mt-2 break-words">
                        {progress.current_model || "Not started"}
                    </p>
                </div>

                <div className="bg-gray-50 rounded-xl p-4">
                    <p className="text-xs text-gray-500">
                        Current Stage
                    </p>

                    <p className="text-sm font-bold text-gray-900 mt-2">
                        {progress.stage || "Waiting"}
                    </p>
                </div>

            </div>

            {/* Execution message */}

            <div className="border-t border-gray-100 pt-4">

                <p className="text-sm text-gray-600">
                    {progress.message || "Waiting for benchmark execution."}
                </p>

                {progress.error && (
                    <div className="mt-3 bg-red-50 border border-red-200 rounded-lg p-3">
                        <p className="text-sm font-semibold text-red-700">
                            Benchmark Error
                        </p>

                        <p className="text-xs text-red-600 mt-1 whitespace-pre-wrap break-words">
                            {progress.error}
                        </p>
                    </div>
                )}

                {status === "completed" && (
                    <p className="text-sm text-emerald-700 font-medium mt-3">
                        All benchmark experiments have finished successfully.
                    </p>
                )}

            </div>

        </section>
    );
}

export default BenchmarkProgress;
