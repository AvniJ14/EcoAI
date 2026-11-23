import { useEffect, useState, useCallback, useMemo } from "react";

import Sidebar from "./components/Sidebar";
import BenchmarkProgress from "./components/BenchmarkProgress";

import {
    getAvailableDatasets,
    getBenchmarkHistory,
    getBenchmarkDetails,
    startBenchmark,
    getBenchmarkStatus
} from "./services/api";

// ------------------------------------------------------------
// Formatting helpers
// ------------------------------------------------------------

const formatNumber = (value, digits = 3) =>
    value == null || !Number.isFinite(Number(value))
        ? "N/A"
        : Number(value).toFixed(digits);

const formatPercent = value =>
    value == null || !Number.isFinite(Number(value))
        ? "N/A"
        : `${(Number(value) * 100).toFixed(2)}%`;

const formatEnergy = value =>
    value == null || !Number.isFinite(Number(value))
        ? "N/A"
        : `${Number(value).toExponential(3)} kWh`;

const formatCarbon = value =>
    value == null || !Number.isFinite(Number(value))
        ? "N/A"
        : `${Number(value).toExponential(3)} kg`;

const formatDate = value =>
    value ? new Date(value).toLocaleString() : "N/A";

const isRegression = benchmark =>
    benchmark?.task_type === "regression";

const qualityValue = (model, regression) =>
    regression ? model.r2_score : model.accuracy;

const qualityLabel = regression => regression ? "R² Score" : "Accuracy";

const qualityDisplay = (model, regression) =>
    regression
        ? formatNumber(model.r2_score, 4)
        : formatPercent(model.accuracy);


// ------------------------------------------------------------
// Reusable UI components
// ------------------------------------------------------------

function StatCard({ title, value, subtitle }) {
    return (
        <div className="bg-[#164638] border border-[#285B49] rounded-xl p-5">
            <p className="text-emerald-100/70 text-sm">{title}</p>

            <h2 className="text-2xl font-bold mt-3 break-words">
                {value}
            </h2>

            <p className="text-emerald-400 text-xs mt-2">
                {subtitle}
            </p>
        </div>
    );
}


function Panel({ title, subtitle, children, className = "" }) {
    return (
        <section className={`bg-[#164638] border border-[#285B49] rounded-xl p-6 ${className}`}>
            <div className="mb-5">
                <h2 className="text-xl font-semibold">{title}</h2>

                {subtitle && (
                    <p className="text-sm text-emerald-100/60 mt-1">
                        {subtitle}
                    </p>
                )}
            </div>

            {children}
        </section>
    );
}


function MetricBar({
    label,
    value,
    display,
    max = 100,
    color = "bg-emerald-400"
}) {
    const numericValue = Number(value);

    const percentage =
        value == null || !Number.isFinite(numericValue) || max <= 0
            ? 0
            : Math.min(100, Math.max(0, (numericValue / max) * 100));

    return (
        <div>
            <div className="flex justify-between gap-3 text-sm mb-2">
                <span className="text-emerald-50">{label}</span>

                <span className="text-emerald-300 font-semibold">
                    {display}
                </span>
            </div>

            <div className="h-3 bg-[#0B2C23] rounded-full overflow-hidden">
                <div
                    className={`${color} h-full rounded-full transition-all duration-700`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
}


function EmptyState({ children }) {
    return (
        <p className="text-emerald-100/60 py-3">
            {children}
        </p>
    );
}


// ------------------------------------------------------------
// Main application
// ------------------------------------------------------------

function App() {

    const [history, setHistory] = useState([]);
    const [benchmark, setBenchmark] = useState(null);
    const [selectedId, setSelectedId] = useState("");

    const [datasets, setDatasets] = useState([]);

    // Benchmark configuration
    const [datasetId, setDatasetId] = useState("breast_cancer");
    const [experimentRuns, setExperimentRuns] = useState(5);
    const [inferenceRepeats, setInferenceRepeats] = useState(100);

    const [activePage, setActivePage] = useState("Dashboard");

    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState("");

    // Benchmark execution states
    const [isPolling, setIsPolling] = useState(false);
    const [runStatus, setRunStatus] = useState(null);
    const [runError, setRunError] = useState("");

    // Live progress
    const [benchmarkProgress, setBenchmarkProgress] = useState(null);

    const selectedDataset = datasets.find(
        item => item.id === datasetId
    );

    const regression = isRegression(benchmark);

    const currentTask =
        benchmark?.task_type ||
        selectedDataset?.task ||
        "classification";


    // --------------------------------------------------------
    // Load available datasets
    // --------------------------------------------------------

    const loadDatasets = useCallback(async () => {

        try {

            const items = await getAvailableDatasets();

            setDatasets(items || []);

            if (
                items?.length &&
                !items.some(item => item.id === datasetId)
            ) {
                setDatasetId(items[0].id);
            }

        } catch (err) {

            console.error("Dataset loading error:", err);

            setError(
                "Unable to load available datasets. Check the backend server."
            );

        }

    }, [datasetId]);


    // --------------------------------------------------------
    // Load dashboard history and latest benchmark
    // --------------------------------------------------------

    const loadDashboard = useCallback(async () => {

        try {

            setError("");
            setRefreshing(true);

            const records = await getBenchmarkHistory();

            const safeRecords = Array.isArray(records)
                ? records
                : [];

            setHistory(safeRecords);

            if (safeRecords.length > 0) {

                const latest = safeRecords[0];

                setSelectedId(String(latest.id));

                const details = await getBenchmarkDetails(latest.id);

                setBenchmark(details);

            } else {

                setBenchmark(null);
                setSelectedId("");

            }

        } catch (err) {

            console.error(err);

            setError(
                "Unable to load benchmark data. Check the backend server."
            );

        } finally {

            setLoading(false);
            setRefreshing(false);

        }

    }, []);


    // Initial loading

    useEffect(() => {

        loadDatasets();
        loadDashboard();

    }, [loadDatasets, loadDashboard]);


    // --------------------------------------------------------
    // Live benchmark progress polling
    // --------------------------------------------------------

    useEffect(() => {

        if (!isPolling) return undefined;

        let timer;
        let cancelled = false;

        const checkStatus = async () => {

            try {

                const result = await getBenchmarkStatus();

                if (cancelled) return;

                setBenchmarkProgress(result);
                setRunStatus(result);
                setRunError(result.error || "");

                // Benchmark completed
                if (result.status === "completed") {

                    setIsPolling(false);

                    await loadDashboard();

                }

                // Benchmark failed
                else if (result.status === "failed") {

                    setIsPolling(false);

                }

                // Continue polling
                else {

                    timer = setTimeout(checkStatus, 2000);

                }

            } catch (err) {

                if (!cancelled) {

                    setIsPolling(false);
                    setRunError(err.message);

                }

            }

        };

        timer = setTimeout(checkStatus, 1000);

        return () => {

            cancelled = true;

            clearTimeout(timer);

        };

    }, [isPolling, loadDashboard]);


    // --------------------------------------------------------
    // Start benchmark
    // --------------------------------------------------------

    const handleStartBenchmark = async () => {

        if (isPolling) return;

        try {

            setRunError("");
            setError("");

            setBenchmarkProgress(null);

            setRunStatus({
                status: "queued",
                message: "Submitting benchmark request..."
            });

            await startBenchmark({

                dataset_id: datasetId,

                experiment_runs: Number(experimentRuns),

                inference_repeats: Number(inferenceRepeats)

            });

            setIsPolling(true);

        } catch (err) {

            setRunStatus({

                status: "failed",

                message: "Unable to start benchmark."

            });

            setRunError(err.message);

        }

    };


    // --------------------------------------------------------
    // Select previous benchmark
    // --------------------------------------------------------

    const handleBenchmarkChange = async event => {

        const id = event.target.value;

        if (!id) return;

        setSelectedId(id);

        try {

            setError("");
            setRefreshing(true);

            const details = await getBenchmarkDetails(id);

            setBenchmark(details);

        } catch (err) {

            console.error(err);

            setError(
                "Unable to load the selected benchmark."
            );

        } finally {

            setRefreshing(false);

        }

    };


    // --------------------------------------------------------
    // Process benchmark data
    // --------------------------------------------------------

    const models = benchmark?.models || [];

    const eligibleModels = useMemo(
        () => models.filter(
            model =>
                model.eligible === true &&
                model.eco_score != null
        ),
        [models]
    );


    const rankedModels = useMemo(
        () => [...eligibleModels].sort(
            (a, b) =>
                Number(b.eco_score) - Number(a.eco_score)
        ),
        [eligibleModels]
    );


    const qualityModels = useMemo(
        () => [...models].sort((a, b) => {

            const aValue = qualityValue(a, regression);
            const bValue = qualityValue(b, regression);

            if (aValue == null) return 1;
            if (bValue == null) return -1;

            return Number(bValue) - Number(aValue);

        }),
        [models, regression]
    );


    const bestModel = rankedModels[0];

    const bestQualityModel = qualityModels.find(
        model => qualityValue(model, regression) != null
    );


    const lowestEnergy = [...models]
        .filter(model => model.energy_consumed_kwh != null)
        .sort(
            (a, b) =>
                Number(a.energy_consumed_kwh) -
                Number(b.energy_consumed_kwh)
        )[0];


    const fastestModel = [...models]
        .filter(model => model.inference_time_seconds != null)
        .sort(
            (a, b) =>
                Number(a.inference_time_seconds) -
                Number(b.inference_time_seconds)
        )[0];


    const lowestCarbon = [...models]
        .filter(model => model.carbon_emissions_kg != null)
        .sort(
            (a, b) =>
                Number(a.carbon_emissions_kg) -
                Number(b.carbon_emissions_kg)
        )[0];


    const averageQuality = models.length
        ? (() => {

            const values = models
                .map(model => qualityValue(model, regression))
                .filter(
                    value =>
                        value != null &&
                        Number.isFinite(Number(value))
                );

            return values.length
                ? values.reduce(
                    (sum, value) => sum + Number(value),
                    0
                ) / values.length
                : null;

        })()
        : null;


    const maxQualityForBar = regression
        ? Math.max(
            1,
            ...qualityModels.map(
                model => Math.max(0, Number(model.r2_score) || 0)
            )
        )
        : 1;


    // --------------------------------------------------------
    // Dashboard statistics
    // --------------------------------------------------------

    const cards = [

        {
            title: "Total Benchmarks",
            value: history.length,
            subtitle: "Saved benchmark runs"
        },

        {
            title: "Models Evaluated",
            value: models.length,
            subtitle: "In selected benchmark"
        },

        {
            title: "Best EcoScore",
            value: bestModel
                ? formatNumber(bestModel.eco_score, 2)
                : "N/A",
            subtitle: bestModel?.model_name || "No eligible model"
        },

        {
            title: `Average ${qualityLabel(regression)}`,
            value: averageQuality == null
                ? "N/A"
                : regression
                    ? formatNumber(averageQuality, 4)
                    : formatPercent(averageQuality),
            subtitle: "Across evaluated models"
        }

    ];


    // --------------------------------------------------------
    // Model recommendations
    // --------------------------------------------------------

    const recommendationItems = [

        {
            title: regression
                ? "Best R² Score"
                : "Best Accuracy",

            model: bestQualityModel,

            metric: bestQualityModel
                ? qualityDisplay(bestQualityModel, regression)
                : "N/A",

            description: regression
                ? "Highest coefficient of determination."
                : "Highest predictive accuracy."
        },

        {
            title: "Lowest Energy",

            model: lowestEnergy,

            metric: lowestEnergy
                ? formatEnergy(lowestEnergy.energy_consumed_kwh)
                : "N/A",

            description: "Lowest estimated energy consumption."
        },

        {
            title: "Fastest Inference",

            model: fastestModel,

            metric: fastestModel
                ? `${formatNumber(fastestModel.inference_time_seconds, 6)} s`
                : "N/A",

            description: "Lowest average inference time."
        },

        {
            title: "Lowest Carbon",

            model: lowestCarbon,

            metric: lowestCarbon
                ? formatCarbon(lowestCarbon.carbon_emissions_kg)
                : "N/A",

            description: "Lowest estimated carbon emissions."
        },

        {
            title: "Best Balanced Model",

            model: bestModel,

            metric: bestModel
                ? `EcoScore ${formatNumber(bestModel.eco_score, 2)}`
                : "N/A",

            description: "Highest EcoScore among eligible models."
        }

    ];


    // --------------------------------------------------------
    // Dashboard overview
    // --------------------------------------------------------

    const renderOverview = () => (

        <>

            {/* Statistics */}

            <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">

                {cards.map(card => (

                    <StatCard
                        key={card.title}
                        {...card}
                    />

                ))}

            </section>


            {/* Model Performance */}

            <section className="grid grid-cols-1 xl:grid-cols-3 gap-5 mb-8">

                <Panel
                    title="Model Performance"
                    subtitle={`${qualityLabel(regression)}, ${regression ? "MAE, RMSE and R²" : "precision, recall and F1"}, and EcoScore`}
                    className="xl:col-span-2"
                >

                    <div className="overflow-x-auto">

                        <table className="w-full text-sm text-left">

                            <thead className="text-emerald-300 border-b border-[#285B49]">

                                <tr>

                                    <th className="py-3 pr-4">Model</th>

                                    <th className="py-3 pr-4">
                                        {qualityLabel(regression)}
                                    </th>

                                    {regression ? (

                                        <>
                                            <th className="py-3 pr-4">MAE</th>
                                            <th className="py-3 pr-4">RMSE</th>
                                        </>

                                    ) : (

                                        <>
                                            <th className="py-3 pr-4">Precision</th>
                                            <th className="py-3 pr-4">F1 Score</th>
                                        </>

                                    )}

                                    <th className="py-3 pr-4">EcoScore</th>

                                    <th className="py-3">Status</th>

                                </tr>

                            </thead>


                            <tbody>

                                {models.map(model => (

                                    <tr
                                        key={model.model_id || model.model_name}
                                        className="border-b border-[#285B49]/60"
                                    >

                                        <td className="py-3 pr-4">
                                            {model.model_name}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {qualityDisplay(model, regression)}
                                        </td>

                                        {regression ? (

                                            <>
                                                <td className="py-3 pr-4">
                                                    {formatNumber(model.mae)}
                                                </td>

                                                <td className="py-3 pr-4">
                                                    {formatNumber(model.rmse)}
                                                </td>
                                            </>

                                        ) : (

                                            <>
                                                <td className="py-3 pr-4">
                                                    {formatNumber(model.precision)}
                                                </td>

                                                <td className="py-3 pr-4">
                                                    {formatNumber(model.f1_score)}
                                                </td>
                                            </>

                                        )}

                                        <td className="py-3 pr-4">
                                            {formatNumber(model.eco_score, 2)}
                                        </td>

                                        <td className="py-3">

                                            <span
                                                className={
                                                    model.eligible
                                                        ? "text-emerald-400"
                                                        : "text-amber-400"
                                                }
                                            >
                                                {model.eligible
                                                    ? "Eligible"
                                                    : "Not eligible"}
                                            </span>

                                        </td>

                                    </tr>

                                ))}

                            </tbody>

                        </table>

                    </div>

                    {models.length === 0 && (
                        <EmptyState>
                            No model results available.
                        </EmptyState>
                    )}

                </Panel>


                {/* Best Eco Model */}

                <Panel
                    title="Best Eco Model"
                    subtitle="Highest eligible EcoScore"
                >

                    {bestModel ? (

                        <>

                            <p className="text-3xl font-bold text-emerald-400">
                                {bestModel.model_name}
                            </p>

                            <p className="text-emerald-100/70 mt-3">
                                EcoScore: {formatNumber(bestModel.eco_score, 2)}
                            </p>

                            <p className="text-emerald-100/70 mt-2">
                                {qualityLabel(regression)}: {qualityDisplay(bestModel, regression)}
                            </p>

                        </>

                    ) : (

                        <EmptyState>
                            No eligible model found.
                        </EmptyState>

                    )}

                </Panel>

            </section>


            {/* Quality and EcoScore */}

            <section className="grid grid-cols-1 xl:grid-cols-2 gap-5 mb-8">

                <Panel title={`${qualityLabel(regression)} Comparison`}>

                    {qualityModels.length ? (

                        <div className="space-y-5">

                            {qualityModels.map(model => (

                                <MetricBar
                                    key={model.model_id || model.model_name}
                                    label={model.model_name}
                                    value={
                                        regression
                                            ? Math.max(0, Number(model.r2_score) || 0)
                                            : (Number(model.accuracy) || 0) * 100
                                    }
                                    max={regression ? maxQualityForBar : 100}
                                    display={qualityDisplay(model, regression)}
                                />

                            ))}

                        </div>

                    ) : (

                        <EmptyState>
                            No quality metrics available.
                        </EmptyState>

                    )}

                </Panel>


                <Panel title="EcoScore Leaderboard">

                    {rankedModels.length ? (

                        <div className="space-y-3">

                            {rankedModels.map((model, index) => (

                                <div
                                    key={model.model_id || model.model_name}
                                    className="flex items-center gap-4 bg-[#0B2C23] rounded-lg p-4"
                                >

                                    <div className="w-9 h-9 flex items-center justify-center rounded-full bg-emerald-500/20 text-emerald-300 font-bold">
                                        {index + 1}
                                    </div>

                                    <div className="flex-1 min-w-0">

                                        <p className="font-semibold">
                                            {model.model_name}
                                        </p>

                                        <p className="text-xs text-emerald-100/60 mt-1">
                                            {qualityLabel(regression)}: {qualityDisplay(model, regression)}
                                        </p>

                                    </div>

                                    <p className="text-xl font-bold text-emerald-400">
                                        {formatNumber(model.eco_score, 2)}
                                    </p>

                                </div>

                            ))}

                        </div>

                    ) : (

                        <EmptyState>
                            No eligible models to rank.
                        </EmptyState>

                    )}

                </Panel>

            </section>

        </>

    );


    // --------------------------------------------------------
    // Model comparison
    // --------------------------------------------------------

    const renderComparison = () => (

        <Panel title="Detailed Model Comparison">

            <div className="overflow-x-auto">

                <table className="w-full text-sm text-left">

                    <thead className="text-emerald-300 border-b border-[#285B49]">

                        <tr>

                            <th className="py-3 pr-4">Model</th>

                            {regression ? (

                                <>
                                    <th className="py-3 pr-4">MAE</th>
                                    <th className="py-3 pr-4">MSE</th>
                                    <th className="py-3 pr-4">RMSE</th>
                                    <th className="py-3 pr-4">R²</th>
                                </>

                            ) : (

                                <>
                                    <th className="py-3 pr-4">Accuracy</th>
                                    <th className="py-3 pr-4">Precision</th>
                                    <th className="py-3 pr-4">Recall</th>
                                    <th className="py-3 pr-4">F1</th>
                                </>

                            )}

                            <th className="py-3 pr-4">Training (s)</th>
                            <th className="py-3 pr-4">Inference (s)</th>
                            <th className="py-3 pr-4">CPU %</th>
                            <th className="py-3">RAM change</th>

                        </tr>

                    </thead>


                    <tbody>

                        {models.map(model => (

                            <tr
                                key={model.model_id || model.model_name}
                                className="border-b border-[#285B49]/60"
                            >

                                <td className="py-3 pr-4">
                                    {model.model_name}
                                </td>

                                {regression ? (

                                    <>
                                        <td className="py-3 pr-4">
                                            {formatNumber(model.mae)}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {formatNumber(model.mse)}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {formatNumber(model.rmse)}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {formatNumber(model.r2_score, 4)}
                                        </td>
                                    </>

                                ) : (

                                    <>
                                        <td className="py-3 pr-4">
                                            {formatPercent(model.accuracy)}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {formatNumber(model.precision)}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {formatNumber(model.recall)}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {formatNumber(model.f1_score)}
                                        </td>
                                    </>

                                )}

                                <td className="py-3 pr-4">
                                    {formatNumber(model.training_time_seconds, 6)}
                                </td>

                                <td className="py-3 pr-4">
                                    {formatNumber(model.inference_time_seconds, 6)}
                                </td>

                                <td className="py-3 pr-4">
                                    {formatNumber(model.cpu_usage_percent)}
                                </td>

                                <td className="py-3">
                                    {formatNumber(model.memory_change_mb)} MB
                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

            {!models.length && (
                <EmptyState>
                    No model results available.
                </EmptyState>
            )}

        </Panel>

    );


    // --------------------------------------------------------
    // Sustainability analytics
    // --------------------------------------------------------

    const renderSustainability = () => {

        const maxEnergy = Math.max(
            0.000001,
            ...models.map(
                model => Number(model.energy_consumed_kwh) || 0
            )
        );

        const maxCarbon = Math.max(
            0.000001,
            ...models.map(
                model => Number(model.carbon_emissions_kg) || 0
            )
        );

        return (

            <>

                <section className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">

                    <Panel title="Energy Consumption">

                        {models.length ? (

                            <div className="space-y-5">

                                {models.map(model => (

                                    <MetricBar
                                        key={model.model_id || model.model_name}
                                        label={model.model_name}
                                        value={model.energy_consumed_kwh}
                                        max={maxEnergy}
                                        display={formatEnergy(model.energy_consumed_kwh)}
                                    />

                                ))}

                            </div>

                        ) : (

                            <EmptyState>
                                No energy data available.
                            </EmptyState>

                        )}

                    </Panel>


                    <Panel title="Carbon Emissions">

                        {models.length ? (

                            <div className="space-y-5">

                                {models.map(model => (

                                    <MetricBar
                                        key={model.model_id || model.model_name}
                                        label={model.model_name}
                                        value={model.carbon_emissions_kg}
                                        max={maxCarbon}
                                        display={formatCarbon(model.carbon_emissions_kg)}
                                        color="bg-teal-300"
                                    />

                                ))}

                            </div>

                        ) : (

                            <EmptyState>
                                No carbon data available.
                            </EmptyState>

                        )}

                    </Panel>

                </section>


                <Panel title="Sustainability Results">

                    <div className="overflow-x-auto">

                        <table className="w-full text-sm text-left">

                            <thead className="text-emerald-300 border-b border-[#285B49]">

                                <tr>
                                    <th className="py-3 pr-4">Model</th>
                                    <th className="py-3 pr-4">Energy</th>
                                    <th className="py-3 pr-4">Carbon</th>
                                    <th className="py-3">EcoScore</th>
                                </tr>

                            </thead>


                            <tbody>

                                {models.map(model => (

                                    <tr
                                        key={model.model_id || model.model_name}
                                        className="border-b border-[#285B49]/60"
                                    >

                                        <td className="py-3 pr-4">
                                            {model.model_name}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {formatEnergy(model.energy_consumed_kwh)}
                                        </td>

                                        <td className="py-3 pr-4">
                                            {formatCarbon(model.carbon_emissions_kg)}
                                        </td>

                                        <td className="py-3">
                                            {formatNumber(model.eco_score, 2)}
                                        </td>

                                    </tr>

                                ))}

                            </tbody>

                        </table>

                    </div>

                    {!models.length && (
                        <EmptyState>
                            No sustainability results available.
                        </EmptyState>
                    )}

                    <p className="text-xs text-emerald-100/50 mt-5">
                        Energy and carbon values are estimates, not direct meter readings.
                    </p>

                </Panel>

            </>

        );

    };


    // --------------------------------------------------------
    // Model recommendations
    // --------------------------------------------------------

    const renderRecommendations = () => (

        <Panel title="Model Recommendations">

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

                {recommendationItems.map(item => (

                    <div
                        key={item.title}
                        className="bg-[#0B2C23] border border-[#285B49] rounded-xl p-5"
                    >

                        <p className="text-emerald-300 text-sm font-semibold">
                            {item.title}
                        </p>

                        <h3 className="text-xl font-bold mt-3">
                            {item.model?.model_name || "Not available"}
                        </h3>

                        <p className="text-emerald-400 font-semibold mt-2">
                            {item.metric}
                        </p>

                        <p className="text-sm text-emerald-100/60 mt-3">
                            {item.description}
                        </p>

                    </div>

                ))}

            </div>

        </Panel>

    );


    // --------------------------------------------------------
    // Benchmark history
    // --------------------------------------------------------

    const renderHistory = () => (

        <Panel title="Benchmark History">

            <div className="overflow-x-auto">

                <table className="w-full text-sm text-left">

                    <thead className="text-emerald-300 border-b border-[#285B49]">

                        <tr>
                            <th className="py-3 pr-4">ID</th>
                            <th className="py-3 pr-4">Dataset</th>
                            <th className="py-3 pr-4">Task</th>
                            <th className="py-3 pr-4">Models</th>
                            <th className="py-3 pr-4">Status</th>
                            <th className="py-3">Created</th>
                        </tr>

                    </thead>


                    <tbody>

                        {history.map(item => (

                            <tr
                                key={item.id}
                                onClick={() =>
                                    handleBenchmarkChange({
                                        target: {
                                            value: String(item.id)
                                        }
                                    })
                                }
                                className={`border-b border-[#285B49]/60 cursor-pointer hover:bg-[#205341] ${
                                    String(item.id) === selectedId
                                        ? "bg-[#205341]"
                                        : ""
                                }`}
                            >

                                <td className="py-3 pr-4">
                                    #{item.id}
                                </td>

                                <td className="py-3 pr-4">
                                    {item.dataset_name}
                                </td>

                                <td className="py-3 pr-4 capitalize">
                                    {item.task_type || "N/A"}
                                </td>

                                <td className="py-3 pr-4">
                                    {item.total_models}
                                </td>

                                <td className="py-3 pr-4">
                                    {item.status}
                                </td>

                                <td className="py-3">
                                    {formatDate(item.created_at)}
                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

            {!history.length && (
                <EmptyState>
                    No benchmark history yet.
                </EmptyState>
            )}

        </Panel>

    );


    // --------------------------------------------------------
    // Page navigation
    // --------------------------------------------------------

    const pageContent = {

        Dashboard: renderOverview,

        "Model Comparison": renderComparison,

        Sustainability: renderSustainability,

        Recommendations: renderRecommendations,

        "Benchmark History": renderHistory

    };


    // --------------------------------------------------------
    // Main application UI
    // --------------------------------------------------------

    return (

        <div className="flex min-h-screen bg-[#071F1A] text-white">

            {/* Sidebar */}

            <Sidebar
                activePage={activePage}
                onNavigate={setActivePage}
            />


            <main className="flex-1 min-w-0 p-5 md:p-8">

                {/* Header */}

                <header className="flex flex-col gap-5 mb-8">

                    <div className="flex flex-wrap justify-between items-center gap-4">

                        <div>

                            <h1 className="text-3xl font-bold">
                                {activePage}
                            </h1>

                            <p className="text-emerald-100/70 mt-2">
                                EcoAI Benchmark | Sustainable AI Analytics
                            </p>

                        </div>


                        <div className="flex flex-wrap gap-3">

                            {/* Benchmark Selector */}

                            <select
                                value={selectedId}
                                onChange={handleBenchmarkChange}
                                className="bg-[#164638] border border-[#285B49] rounded-lg px-3 py-3 text-sm"
                                disabled={
                                    history.length === 0 ||
                                    isPolling
                                }
                                aria-label="Select previous benchmark"
                            >

                                {history.length === 0 && (
                                    <option value="">
                                        No benchmarks
                                    </option>
                                )}

                                {history.map(item => (

                                    <option
                                        key={item.id}
                                        value={item.id}
                                    >
                                        Benchmark #{item.id}
                                    </option>

                                ))}

                            </select>


                            {/* Refresh Button */}

                            <button
                                onClick={loadDashboard}
                                disabled={refreshing}
                                className="bg-[#205341] hover:bg-[#28674F] disabled:opacity-50 px-4 py-3 rounded-lg transition"
                            >
                                {refreshing
                                    ? "Refreshing..."
                                    : "↻ Refresh"}
                            </button>

                        </div>

                    </div>


                    {/* Benchmark Configuration */}

                    <Panel
                        title="Configure Benchmark"
                        subtitle="Choose a dataset and evaluation settings before starting an experiment."
                    >

                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">

                            {/* Dataset Selector */}

                            <div>

                                <label className="block text-sm text-emerald-100/70 mb-2">
                                    Dataset
                                </label>

                                <select
                                    value={datasetId}
                                    onChange={event => setDatasetId(event.target.value)}
                                    disabled={isPolling || datasets.length === 0}
                                    className="w-full bg-[#0B2C23] border border-[#285B49] rounded-lg px-3 py-3 text-sm"
                                >

                                    {datasets.map(dataset => (

                                        <option
                                            key={dataset.id}
                                            value={dataset.id}
                                        >
                                            {dataset.name} ({dataset.task})
                                        </option>

                                    ))}

                                </select>

                            </div>


                            {/* Experiment Runs */}

                            <div>

                                <label className="block text-sm text-emerald-100/70 mb-2">
                                    Experiment Runs
                                </label>

                                <input
                                    type="number"
                                    min="1"
                                    max="20"
                                    value={experimentRuns}
                                    onChange={event => setExperimentRuns(event.target.value)}
                                    disabled={isPolling}
                                    className="w-full bg-[#0B2C23] border border-[#285B49] rounded-lg px-3 py-3 text-sm"
                                />

                            </div>


                            {/* Inference Repeats */}

                            <div>

                                <label className="block text-sm text-emerald-100/70 mb-2">
                                    Inference Repeats
                                </label>

                                <input
                                    type="number"
                                    min="1"
                                    max="1000"
                                    value={inferenceRepeats}
                                    onChange={event => setInferenceRepeats(event.target.value)}
                                    disabled={isPolling}
                                    className="w-full bg-[#0B2C23] border border-[#285B49] rounded-lg px-3 py-3 text-sm"
                                />

                            </div>


                            {/* Start Benchmark Button */}

                            <button
                                onClick={handleStartBenchmark}
                                disabled={
                                    isPolling ||
                                    !datasetId ||
                                    Number(experimentRuns) < 1 ||
                                    Number(experimentRuns) > 20 ||
                                    Number(inferenceRepeats) < 1 ||
                                    Number(inferenceRepeats) > 1000
                                }
                                className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed px-5 py-3 rounded-lg font-semibold text-[#062B20] transition"
                            >
                                {isPolling
                                    ? "Benchmark Running..."
                                    : "+ Start Benchmark"}
                            </button>

                        </div>


                        {selectedDataset && (

                            <p className="text-xs text-emerald-100/60 mt-4">

                                Selected task:

                                <span className="text-emerald-300 capitalize">
                                    {" "}{selectedDataset.task}
                                </span>

                                . The dashboard will display the metrics relevant to this task.

                            </p>

                        )}

                    </Panel>

                </header>


                {/* Live Benchmark Progress */}

                {(isPolling || benchmarkProgress) && (

                    <div className="mb-6">

                        <BenchmarkProgress
                            progress={benchmarkProgress || runStatus}
                        />

                    </div>

                )}


                {/* Benchmark Error */}

                {runError && !isPolling && (

                    <div className="mb-6 bg-red-900/30 border border-red-500/40 rounded-xl p-4">

                        <p className="font-semibold text-red-300">
                            Benchmark Execution Error
                        </p>

                        <p className="text-sm text-red-200 mt-2 whitespace-pre-wrap break-words">
                            {runError}
                        </p>

                    </div>

                )}


                {/* Loading and Error States */}

                {loading ? (

                    <div className="text-emerald-300 py-10">
                        Loading benchmark data...
                    </div>

                ) : error ? (

                    <div className="bg-red-900/30 border border-red-500/40 rounded-xl p-5 text-red-300">
                        {error}
                    </div>

                ) : !benchmark ? (

                    <Panel title="No benchmark data">

                        <p className="text-emerald-100/70">
                            Select a dataset above and start a benchmark to see your results here.
                        </p>

                    </Panel>

                ) : (

                    <>

                        {/* Selected Benchmark Information */}

                        <div className="mb-5 text-sm text-emerald-100/60">

                            Dataset:

                            <span className="text-emerald-300">
                                {" "}{benchmark.dataset_name}
                            </span>

                            {" | "}

                            Task:

                            <span className="text-emerald-300 capitalize">
                                {" "}{currentTask}
                            </span>

                            {" | "}

                            Benchmark ID:

                            <span className="text-emerald-300">
                                {" "}#{benchmark.id}
                            </span>

                        </div>


                        {/* Active Page */}

                        {pageContent[activePage]
                            ? pageContent[activePage]()
                            : renderOverview()}

                    </>

                )}


                {/* Footer */}

                <footer className="mt-10 border-t border-[#285B49] pt-5 text-xs text-emerald-100/40">

                    EcoAI Benchmark v1.0 | Sustainability metrics are estimates.

                </footer>

            </main>

        </div>

    );

}


export default App;