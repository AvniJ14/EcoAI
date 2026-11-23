
from app.database.database import SessionLocal

from app.models.benchmark import (
    BenchmarkRun,
    ModelResult,
    ExperimentMetric
)


# ==================================================
# 1. SAVE BENCHMARK RESULTS
# ==================================================

def save_benchmark_results(results, ranked_results):

    if not results:
        raise ValueError("No benchmark results to save.")

    first_result = results[0]

    dataset_id = first_result.get("dataset_id")
    dataset_name = first_result.get(
        "dataset",
        "Unknown Dataset"
    )

    task_type = first_result.get(
        "task_type",
        "classification"
    )

    experiment_runs = first_result.get(
        "experiment_runs",
        5
    )

    inference_repeats = first_result.get(
        "inference_repeats",
        100
    )

    db = SessionLocal()

    try:

        # ==========================================
        # 2. CREATE BENCHMARK RECORD
        # ==========================================

        benchmark = BenchmarkRun(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            task_type=task_type,
            total_models=len(results),
            experiment_runs=experiment_runs,
            inference_repeats=inference_repeats,
            status="Completed"
        )

        db.add(benchmark)
        db.flush()

        # ==========================================
        # 3. SAVE MODEL RESULTS
        # ==========================================

        for model in ranked_results:

            model_record = ModelResult(

                benchmark_id=benchmark.id,

                model_id=model.get("model_id"),
                model_name=model["model_name"],

                task_type=model.get(
                    "task_type",
                    task_type
                ),

                # Classification
                accuracy=model.get("accuracy"),
                precision=model.get("precision"),
                recall=model.get("recall"),
                f1_score=model.get("f1_score"),

                accuracy_std=model.get("accuracy_std"),
                precision_std=model.get("precision_std"),
                recall_std=model.get("recall_std"),
                f1_score_std=model.get("f1_score_std"),

                # Regression
                mae=model.get("mae"),
                mse=model.get("mse"),
                rmse=model.get("rmse"),
                r2_score=model.get("r2_score"),

                mae_std=model.get("mae_std"),
                mse_std=model.get("mse_std"),
                rmse_std=model.get("rmse_std"),
                r2_score_std=model.get("r2_score_std"),

                # Time
                training_time_seconds=model.get(
                    "training_time_seconds"
                ),

                training_time_std_seconds=model.get(
                    "training_time_std_seconds"
                ),

                inference_time_seconds=model.get(
                    "inference_time_seconds"
                ),

                median_inference_time_seconds=model.get(
                    "median_inference_time_seconds"
                ),

                inference_time_std_seconds=model.get(
                    "inference_time_std_seconds"
                ),

                # Resources
                cpu_usage_percent=model.get(
                    "cpu_usage_percent"
                ),

                memory_before_mb=model.get(
                    "memory_before_mb"
                ),

                memory_after_mb=model.get(
                    "memory_after_mb"
                ),

                memory_change_mb=model.get(
                    "memory_change_mb"
                ),

                # Energy
                training_energy_kwh=model.get(
                    "training_energy_kwh"
                ),

                inference_energy_kwh=model.get(
                    "inference_energy_kwh"
                ),

                energy_consumed_kwh=model.get(
                    "energy_consumed_kwh"
                ),

                energy_std_kwh=model.get(
                    "energy_std_kwh"
                ),

                # Carbon
                training_carbon_kg=model.get(
                    "training_carbon_kg"
                ),

                inference_carbon_kg=model.get(
                    "inference_carbon_kg"
                ),

                carbon_emissions_kg=model.get(
                    "carbon_emissions_kg"
                ),

                # EcoScore
                accuracy_percentage=model.get(
                    "accuracy_percentage"
                ),

                r2_percentage=model.get(
                    "r2_percentage"
                ),

                quality_score=model.get(
                    "quality_score"
                ),

                energy_efficiency_score=model.get(
                    "energy_efficiency_score"
                ),

                eco_score=model.get("eco_score"),

                eligible=model.get("eligible", False),

                rank=model.get("rank"),

                recommendation_status=model.get(
                    "recommendation_status"
                ),

                eligibility_reason=model.get(
                    "eligibility_reason"
                )
            )

            db.add(model_record)
            db.flush()

            # ======================================
            # 4. SAVE INDIVIDUAL EXPERIMENTS
            # ======================================

            for run in model.get("run_details", []):

                experiment = ExperimentMetric(

                    model_result_id=model_record.id,

                    run_number=run.get("run_number"),

                    # Classification
                    accuracy=run.get("accuracy"),
                    precision=run.get("precision"),
                    recall=run.get("recall"),
                    f1_score=run.get("f1_score"),

                    # Regression
                    mae=run.get("mae"),
                    mse=run.get("mse"),
                    rmse=run.get("rmse"),
                    r2_score=run.get("r2_score"),

                    # Time
                    training_time_seconds=run.get(
                        "training_time"
                    ),

                    inference_time_seconds=run.get(
                        "inference_time"
                    ),

                    total_inference_time_seconds=run.get(
                        "total_inference_time"
                    ),

                    # Resources
                    cpu_usage_percent=run.get(
                        "cpu_usage"
                    ),

                    memory_before_mb=run.get(
                        "memory_before"
                    ),

                    memory_after_mb=run.get(
                        "memory_after"
                    ),

                    memory_change_mb=run.get(
                        "memory_change"
                    ),

                    # Energy
                    training_energy_kwh=run.get(
                        "training_energy"
                    ),

                    inference_energy_kwh=run.get(
                        "inference_energy"
                    ),

                    total_energy_kwh=run.get(
                        "total_energy"
                    ),

                    # Carbon
                    training_carbon_kg=run.get(
                        "training_carbon"
                    ),

                    inference_carbon_kg=run.get(
                        "inference_carbon"
                    ),

                    total_carbon_kg=run.get(
                        "total_carbon"
                    )
                )

                db.add(experiment)

        # ==========================================
        # 5. COMMIT
        # ==========================================

        db.commit()

        print("\n========== DATABASE STORAGE ==========")
        print("Benchmark results saved successfully!")
        print(f"Benchmark ID: {benchmark.id}")
        print(f"Dataset: {dataset_name}")
        print(f"Task: {task_type}")
        print(f"Models saved: {len(ranked_results)}")

        total_experiments = sum(
            len(model.get("run_details", []))
            for model in ranked_results
        )

        print(
            f"Experiment records saved: {total_experiments}"
        )

        return benchmark.id

    except Exception as error:

        db.rollback()

        print("\nDatabase storage failed!")
        print(f"Reason: {error}")

        raise

    finally:
        db.close()


# ==================================================
# 6. GET BENCHMARK HISTORY
# ==================================================

def get_benchmark_history():

    db = SessionLocal()

    try:

        benchmarks = (
            db.query(BenchmarkRun)
            .order_by(BenchmarkRun.created_at.desc())
            .all()
        )

        history = []

        for benchmark in benchmarks:

            history.append({

                "id": benchmark.id,

                "dataset_id": benchmark.dataset_id,

                "dataset_name": benchmark.dataset_name,

                "task_type": benchmark.task_type,

                "total_models": benchmark.total_models,

                "experiment_runs": benchmark.experiment_runs,

                "inference_repeats": benchmark.inference_repeats,

                "status": benchmark.status,

                "created_at": (
                    benchmark.created_at.isoformat()
                    if benchmark.created_at else None
                )
            })

        return history

    finally:
        db.close()


# ==================================================
# 7. GET SPECIFIC BENCHMARK DETAILS
# ==================================================

def get_benchmark_details(benchmark_id):

    db = SessionLocal()

    try:

        benchmark = (
            db.query(BenchmarkRun)
            .filter(BenchmarkRun.id == benchmark_id)
            .first()
        )

        if benchmark is None:
            return None

        details = {

            "id": benchmark.id,

            "dataset_id": benchmark.dataset_id,

            "dataset_name": benchmark.dataset_name,

            "task_type": benchmark.task_type,

            "total_models": benchmark.total_models,

            "experiment_runs": benchmark.experiment_runs,

            "inference_repeats": benchmark.inference_repeats,

            "status": benchmark.status,

            "created_at": (
                benchmark.created_at.isoformat()
                if benchmark.created_at else None
            ),

            "models": []
        }

        for model in benchmark.model_results:

            model_data = {

                "model_id": model.model_id,

                "model_name": model.model_name,

                "task_type": model.task_type,

                # Classification
                "accuracy": model.accuracy,
                "precision": model.precision,
                "recall": model.recall,
                "f1_score": model.f1_score,

                # Regression
                "mae": model.mae,
                "mse": model.mse,
                "rmse": model.rmse,
                "r2_score": model.r2_score,

                # Time
                "training_time_seconds": (
                    model.training_time_seconds
                ),

                "inference_time_seconds": (
                    model.inference_time_seconds
                ),

                # Resources
                "cpu_usage_percent": model.cpu_usage_percent,

                "memory_change_mb": model.memory_change_mb,

                # Sustainability
                "energy_consumed_kwh": (
                    model.energy_consumed_kwh
                ),

                "carbon_emissions_kg": (
                    model.carbon_emissions_kg
                ),

                # EcoScore
                "accuracy_percentage": (
                    model.accuracy_percentage
                ),

                "r2_percentage": model.r2_percentage,

                "quality_score": model.quality_score,

                "energy_efficiency_score": (
                    model.energy_efficiency_score
                ),

                "eco_score": model.eco_score,

                "eligible": model.eligible,

                "rank": model.rank,

                "recommendation_status": (
                    model.recommendation_status
                ),

                "eligibility_reason": (
                    model.eligibility_reason
                ),

                "experiments": []
            }

            for experiment in model.experiment_metrics:

                model_data["experiments"].append({

                    "run_number": experiment.run_number,

                    # Classification
                    "accuracy": experiment.accuracy,
                    "precision": experiment.precision,
                    "recall": experiment.recall,
                    "f1_score": experiment.f1_score,

                    # Regression
                    "mae": experiment.mae,
                    "mse": experiment.mse,
                    "rmse": experiment.rmse,
                    "r2_score": experiment.r2_score,

                    # Time
                    "training_time_seconds": (
                        experiment.training_time_seconds
                    ),

                    "inference_time_seconds": (
                        experiment.inference_time_seconds
                    ),

                    "total_inference_time_seconds": (
                        experiment.total_inference_time_seconds
                    ),

                    # Resources
                    "cpu_usage_percent": (
                        experiment.cpu_usage_percent
                    ),

                    "memory_before_mb": (
                        experiment.memory_before_mb
                    ),

                    "memory_after_mb": (
                        experiment.memory_after_mb
                    ),

                    "memory_change_mb": (
                        experiment.memory_change_mb
                    ),

                    # Energy
                    "training_energy_kwh": (
                        experiment.training_energy_kwh
                    ),

                    "inference_energy_kwh": (
                        experiment.inference_energy_kwh
                    ),

                    "total_energy_kwh": (
                        experiment.total_energy_kwh
                    ),

                    # Carbon
                    "training_carbon_kg": (
                        experiment.training_carbon_kg
                    ),

                    "inference_carbon_kg": (
                        experiment.inference_carbon_kg
                    ),

                    "total_carbon_kg": (
                        experiment.total_carbon_kg
                    )
                })

            details["models"].append(model_data)

        return details

    finally:
        db.close()
