
# ============================================================
# ECOAI BENCHMARK
# Sustainable Machine Learning Model Evaluation
# Multi-Dataset Classification and Regression
# ============================================================

import time
import statistics

from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.benchmark.dataset_loader import (
    load_dataset,
    DATASET_REGISTRY
)

from app.benchmark.model_registry import get_models

from app.benchmark.evaluation import evaluate_model

from app.database.operations import save_benchmark_results

from app.monitoring.resource_monitor import ResourceMonitor
from app.monitoring.energy_monitor import EnergyMonitor

from app.recommendation.eco_score import EcoScoreCalculator
from app.recommendation.model_recommender import ModelRecommender

from app.benchmark.progress import (
    start_progress,
    update_model_progress,
    complete_experiment,
    complete_model,
    finish_progress,
    fail_progress
)


# Models that benefit from feature scaling.
SCALED_MODELS = {
    "logistic_regression",
    "svm",
    "knn",
    "linear_regression",
    "ridge",
    "svr"
}


# ============================================================
# 1. BENCHMARK RUNNER
# ============================================================

class BenchmarkRunner:

    def __init__(
        self,
        dataset_id="breast_cancer",
        experiment_runs=5,
        inference_repeats=100
    ):

        if dataset_id not in DATASET_REGISTRY:
            raise ValueError(
                f"Unsupported dataset: {dataset_id}"
            )

        if experiment_runs < 1:
            raise ValueError(
                "Experiment runs must be at least 1."
            )

        if inference_repeats < 1:
            raise ValueError(
                "Inference repetitions must be at least 1."
            )

        self.dataset_id = dataset_id
        self.dataset_name = DATASET_REGISTRY[dataset_id]["name"]
        self.task_type = DATASET_REGISTRY[dataset_id]["task"]

        self.experiment_runs = experiment_runs
        self.inference_repeats = inference_repeats

        self.models = get_models(self.task_type)

    # ========================================================
    # 2. PREPARE MODEL
    # ========================================================

    def prepare_model(self, model_id, model):

        fresh_model = clone(model)

        if model_id in SCALED_MODELS:

            return Pipeline([
                ("scaler", StandardScaler()),
                ("estimator", fresh_model)
            ])

        return fresh_model

    # ========================================================
    # 3. LOAD DATASET
    # ========================================================

    def load_dataset(self):

        data = load_dataset(self.dataset_id)

        self.dataset_name = data["dataset_name"]
        self.task_type = data["task_type"]

        X_train = data["X_train"]
        X_test = data["X_test"]
        y_train = data["y_train"]
        y_test = data["y_test"]

        print("\n========== DATASET INFORMATION ==========")

        print(f"Dataset: {self.dataset_name}")
        print(f"Dataset ID: {self.dataset_id}")
        print(f"Task: {self.task_type}")
        print(f"Total samples: {data['total_samples']}")
        print(f"Training samples: {data['training_samples']}")
        print(f"Testing samples: {data['testing_samples']}")
        print(f"Features: {data['total_features']}")

        return X_train, X_test, y_train, y_test

    # ========================================================
    # 4. SAFE ENERGY CALCULATIONS
    # ========================================================

    @staticmethod
    def add_energy(training_value, inference_value):

        if training_value is None or inference_value is None:
            return None

        return training_value + inference_value

    # ========================================================
    # 5. RUN BENCHMARK
    # ========================================================

    def run_benchmark(self):

        X_train, X_test, y_train, y_test = self.load_dataset()

        benchmark_results = []

        print("\n" + "=" * 65)
        print("ECOAI BENCHMARK: INITIALIZATION")
        print("=" * 65)

        print(f"Dataset: {self.dataset_name}")
        print(f"Task: {self.task_type}")
        print(f"Models: {len(self.models)}")
        print(f"Experiment runs: {self.experiment_runs}")
        print(f"Inference repetitions: {self.inference_repeats}")

        # ====================================================
        # 6. WARM-UP
        # ====================================================

        print("\n========== WARM-UP PHASE ==========")

        for model_id, details in self.models.items():

            model_name = details["name"]

            update_model_progress(
                model_name,
                stage="Warm-up"
            )

            try:

                warmup_model = self.prepare_model(
                    model_id,
                    details["model"]
                )

                warmup_model.fit(X_train, y_train)
                warmup_model.predict(X_test)

                print(f"[SUCCESS] {model_name}")

            except Exception as error:

                print(f"[WARNING] Warm-up failed: {model_name}")
                print(f"Reason: {error}")

        # ====================================================
        # 7. ENERGY MONITOR
        # ====================================================

        energy_monitor = EnergyMonitor()
        energy_monitor.start_monitoring()

        try:

            # ================================================
            # 8. MODEL-WISE BENCHMARKING
            # ================================================

            for model_id, details in self.models.items():

                model_name = details["name"]
                base_model = details["model"]

                update_model_progress(
                    model_name,
                    stage="Preparing experiments"
                )

                print("\n" + "=" * 65)
                print(f"BENCHMARKING MODEL: {model_name}")
                print("=" * 65)

                run_metrics = []
                failed_runs = []

                # ============================================
                # 9. REPEATED EXPERIMENTS
                # ============================================

                for run_number in range(
                    1,
                    self.experiment_runs + 1
                ):

                    update_model_progress(
                        model_name,
                        stage=(
                            f"Experiment {run_number}/"
                            f"{self.experiment_runs}"
                        )
                    )

                    print(
                        f"\nExperiment {run_number}/"
                        f"{self.experiment_runs}"
                    )

                    current_model = self.prepare_model(
                        model_id,
                        base_model
                    )

                    training_task = (
                        f"{model_id}_training_{run_number}"
                    )

                    inference_task = (
                        f"{model_id}_inference_{run_number}"
                    )

                    training_task_active = False
                    inference_task_active = False

                    try:

                        # ====================================
                        # 10. TRAINING
                        # ====================================

                        update_model_progress(
                            model_name,
                            stage=f"Training experiment {run_number}"
                        )

                        energy_monitor.start_task(training_task)
                        training_task_active = True

                        training_start = time.perf_counter()

                        current_model.fit(X_train, y_train)

                        training_time = (
                            time.perf_counter() - training_start
                        )

                        training_energy = energy_monitor.stop_task(
                            training_task
                        )

                        training_task_active = False

                        # ====================================
                        # 11. INFERENCE
                        # ====================================

                        update_model_progress(
                            model_name,
                            stage=f"Inference experiment {run_number}"
                        )

                        energy_monitor.start_task(inference_task)
                        inference_task_active = True

                        resource_monitor = ResourceMonitor()
                        resource_monitor.start_monitoring()

                        inference_start = time.perf_counter()

                        for _ in range(self.inference_repeats):

                            predictions = current_model.predict(X_test)

                        total_inference_time = (
                            time.perf_counter() - inference_start
                        )

                        resource_metrics = (
                            resource_monitor.stop_monitoring()
                        )

                        inference_energy = energy_monitor.stop_task(
                            inference_task
                        )

                        inference_task_active = False

                        average_latency = (
                            total_inference_time /
                            self.inference_repeats
                        )

                        # ====================================
                        # 12. EVALUATION
                        # ====================================

                        evaluation = evaluate_model(
                            y_test,
                            predictions,
                            self.task_type
                        )

                        # ====================================
                        # 13. ENERGY AND CARBON
                        # ====================================

                        training_kwh = training_energy.get(
                            "energy_consumed_kwh"
                        )

                        inference_kwh = inference_energy.get(
                            "energy_consumed_kwh"
                        )

                        training_carbon = training_energy.get(
                            "carbon_emissions_kg"
                        )

                        inference_carbon = inference_energy.get(
                            "carbon_emissions_kg"
                        )

                        total_energy = self.add_energy(
                            training_kwh,
                            inference_kwh
                        )

                        total_carbon = self.add_energy(
                            training_carbon,
                            inference_carbon
                        )

                        # ====================================
                        # 14. INDIVIDUAL RUN RESULT
                        # ====================================

                        run_result = {
                            "run_number": run_number,

                            "training_time": training_time,

                            "inference_time": average_latency,

                            "total_inference_time": total_inference_time,

                            # Classification metrics
                            "accuracy": evaluation.get("accuracy"),
                            "precision": evaluation.get("precision"),
                            "recall": evaluation.get("recall"),
                            "f1_score": evaluation.get("f1_score"),

                            # Regression metrics
                            "mae": evaluation.get("mae"),
                            "mse": evaluation.get("mse"),
                            "rmse": evaluation.get("rmse"),
                            "r2_score": evaluation.get("r2_score"),

                            # Resource metrics
                            "cpu_usage": resource_metrics[
                                "cpu_usage_percent"
                            ],

                            "memory_before": resource_metrics[
                                "memory_before_mb"
                            ],

                            "memory_after": resource_metrics[
                                "memory_after_mb"
                            ],

                            "memory_change": resource_metrics[
                                "memory_change_mb"
                            ],

                            # Energy
                            "training_energy": training_kwh,
                            "inference_energy": inference_kwh,
                            "total_energy": total_energy,

                            # Carbon
                            "training_carbon": training_carbon,
                            "inference_carbon": inference_carbon,
                            "total_carbon": total_carbon
                        }

                        run_metrics.append(run_result)

                        # ====================================
                        # 15. DISPLAY EXPERIMENT
                        # ====================================

                        print(
                            f"Training time: {training_time:.6f} seconds"
                        )

                        print(
                            f"Inference latency: {average_latency:.6f} seconds"
                        )

                        print(
                            f"Evaluation metrics: {evaluation}"
                        )

                        print(
                            f"Energy: {total_energy} kWh"
                        )

                        print(
                            f"CPU usage: "
                            f"{resource_metrics['cpu_usage_percent']}%"
                        )

                    except Exception as error:

                        # Close active energy tasks.

                        if training_task_active:

                            try:
                                energy_monitor.stop_task(training_task)
                            except Exception:
                                pass

                        if inference_task_active:

                            try:
                                energy_monitor.stop_task(inference_task)
                            except Exception:
                                pass

                        failed_runs.append({
                            "run_number": run_number,
                            "error": str(error)
                        })

                        print(
                            f"[ERROR] Run {run_number} failed: {error}"
                        )

                    finally:

                        # Count successful and failed attempts.
                        complete_experiment(model_name)

                # ============================================
                # 16. AGGREGATE RESULTS
                # ============================================

                if not run_metrics:

                    print(
                        f"[FAILED] No successful experiments "
                        f"for {model_name}"
                    )

                    complete_model(model_name)
                    continue

                def values(metric):

                    return [
                        run[metric]
                        for run in run_metrics
                        if run.get(metric) is not None
                    ]

                def average(metric):

                    data = values(metric)

                    return (
                        statistics.mean(data)
                        if data else None
                    )

                def median(metric):

                    data = values(metric)

                    return (
                        statistics.median(data)
                        if data else None
                    )

                def deviation(metric):

                    data = values(metric)

                    if len(data) > 1:
                        return statistics.stdev(data)

                    return 0.0 if data else None

                def rounded_average(metric, digits=6):

                    result = average(metric)

                    return (
                        round(result, digits)
                        if result is not None else None
                    )

                def rounded_deviation(metric, digits=6):

                    result = deviation(metric)

                    return (
                        round(result, digits)
                        if result is not None else None
                    )

                # ============================================
                # 17. FINAL MODEL RESULT
                # ============================================

                result = {

                    "model_name": model_name,
                    "model_id": model_id,

                    "dataset": self.dataset_name,
                    "dataset_id": self.dataset_id,
                    "task_type": self.task_type,

                    "experiment_runs": self.experiment_runs,
                    "successful_runs": len(run_metrics),
                    "failed_runs": failed_runs,
                    "inference_repeats": self.inference_repeats,

                    # Training
                    "training_time_seconds": rounded_average(
                        "training_time"
                    ),

                    "training_time_std_seconds": rounded_deviation(
                        "training_time"
                    ),

                    # Inference
                    "inference_time_seconds": rounded_average(
                        "inference_time"
                    ),

                    "median_inference_time_seconds": (
                        round(median("inference_time"), 6)
                        if median("inference_time") is not None
                        else None
                    ),

                    "inference_time_std_seconds": rounded_deviation(
                        "inference_time"
                    ),

                    # Classification
                    "accuracy": rounded_average("accuracy", 4),
                    "precision": rounded_average("precision", 4),
                    "recall": rounded_average("recall", 4),
                    "f1_score": rounded_average("f1_score", 4),

                    "accuracy_std": rounded_deviation("accuracy", 4),
                    "precision_std": rounded_deviation("precision", 4),
                    "recall_std": rounded_deviation("recall", 4),
                    "f1_score_std": rounded_deviation("f1_score", 4),

                    # Regression
                    "mae": rounded_average("mae", 6),
                    "mse": rounded_average("mse", 6),
                    "rmse": rounded_average("rmse", 6),
                    "r2_score": rounded_average("r2_score", 6),

                    "mae_std": rounded_deviation("mae", 6),
                    "mse_std": rounded_deviation("mse", 6),
                    "rmse_std": rounded_deviation("rmse", 6),
                    "r2_score_std": rounded_deviation("r2_score", 6),

                    # Resources
                    "cpu_usage_percent": rounded_average(
                        "cpu_usage", 2
                    ),

                    "memory_before_mb": rounded_average(
                        "memory_before", 2
                    ),

                    "memory_after_mb": rounded_average(
                        "memory_after", 2
                    ),

                    "memory_change_mb": rounded_average(
                        "memory_change", 2
                    ),

                    # Energy
                    "training_energy_kwh": rounded_average(
                        "training_energy", 10
                    ),

                    "inference_energy_kwh": rounded_average(
                        "inference_energy", 10
                    ),

                    "energy_consumed_kwh": rounded_average(
                        "total_energy", 10
                    ),

                    "energy_std_kwh": rounded_deviation(
                        "total_energy", 10
                    ),

                    # Carbon
                    "training_carbon_kg": rounded_average(
                        "training_carbon", 10
                    ),

                    "inference_carbon_kg": rounded_average(
                        "inference_carbon", 10
                    ),

                    "carbon_emissions_kg": rounded_average(
                        "total_carbon", 10
                    ),

                    # Individual experiments
                    "run_details": run_metrics
                }

                benchmark_results.append(result)

                # ============================================
                # 18. MODEL SUMMARY
                # ============================================

                print("\n---------- MODEL SUMMARY ----------")

                print(f"Model: {model_name}")
                print(f"Task: {self.task_type}")

                print(
                    f"Successful runs: "
                    f"{len(run_metrics)}/{self.experiment_runs}"
                )

                print(f"Evaluation metrics: {evaluation}")

                print(
                    f"Training time: "
                    f"{result['training_time_seconds']} seconds"
                )

                print(
                    f"Inference latency: "
                    f"{result['inference_time_seconds']} seconds"
                )

                print(
                    f"Energy: {result['energy_consumed_kwh']} kWh"
                )

                print(
                    f"Carbon: {result['carbon_emissions_kg']} kg"
                )

                complete_model(model_name)

        finally:

            energy_monitor.stop_monitoring()

        print("\n" + "=" * 65)
        print("ALL BENCHMARK EXPERIMENTS COMPLETED")
        print("=" * 65)

        return benchmark_results


# ============================================================
# 19. COMPLETE BENCHMARK WORKFLOW
# ============================================================

def run_full_benchmark(
    dataset_id="breast_cancer",
    experiment_runs=5,
    inference_repeats=100
):

    runner = BenchmarkRunner(
        dataset_id=dataset_id,
        experiment_runs=experiment_runs,
        inference_repeats=inference_repeats
    )

    start_progress(
        total_models=len(runner.models),
        experiments_per_model=runner.experiment_runs
    )

    try:

        print("\n")
        print("=" * 65)
        print("             ECOAI BENCHMARK SYSTEM")
        print("       Sustainable AI Model Evaluation")
        print("=" * 65)

        print(f"Dataset: {runner.dataset_name}")
        print(f"Task: {runner.task_type}")

        # ================================================
        # 20. RUN EXPERIMENTS
        # ================================================

        results = runner.run_benchmark()

        if not results:
            raise RuntimeError(
                "No benchmark results were generated."
            )

        # ================================================
        # 21. ECO SCORE
        # ================================================

        print("\n========== ECOAI MODEL RANKING ==========")

        eco_calculator = EcoScoreCalculator(
            accuracy_weight=0.60,
            energy_weight=0.40,
            min_accuracy=95,
            min_r2=0.70
        )

        ranked_results = eco_calculator.calculate_scores(
            results,
            task_type=runner.task_type
        )

        # ================================================
        # 22. SAVE RESULTS
        # ================================================

        save_benchmark_results(
            results,
            ranked_results
        )

        print("\nBenchmark results saved successfully.")

        # ================================================
        # 23. DISPLAY MODEL RANKING
        # ================================================

        quality_label = (
            "Accuracy"
            if runner.task_type == "classification"
            else "R2 Score"
        )

        quality_key = (
            "accuracy_percentage"
            if runner.task_type == "classification"
            else "r2_percentage"
        )

        print("\n========== ELIGIBLE MODELS ==========")

        eligible_models = [
            model for model in ranked_results
            if model.get("eligible")
        ]

        for model in eligible_models:

            print("\n-----------------------------------")

            print(f"Rank: {model['rank']}")
            print(f"Model: {model['model_name']}")

            print(
                f"{quality_label}: "
                f"{model.get(quality_key)}"
            )

            print(
                f"Energy: {model.get('energy_consumed_kwh')} kWh"
            )

            print(
                f"Carbon: {model.get('carbon_emissions_kg')} kg"
            )

            print(
                f"Energy Efficiency: "
                f"{model.get('energy_efficiency_score')}"
            )

            print(f"EcoScore: {model.get('eco_score')}")

        # ================================================
        # 24. INELIGIBLE MODELS
        # ================================================

        print("\n========== INELIGIBLE MODELS ==========")

        ineligible_models = [
            model for model in ranked_results
            if not model.get("eligible")
        ]

        for model in ineligible_models:

            print("\n-----------------------------------")

            print(f"Model: {model['model_name']}")

            print(
                f"{quality_label}: "
                f"{model.get(quality_key, 'N/A')}"
            )

            print(
                f"Status: {model.get('recommendation_status')}"
            )

            print(
                f"Reason: {model.get('eligibility_reason')}"
            )

        # ================================================
        # 25. RECOMMENDATIONS
        # ================================================

        recommender = ModelRecommender()

        recommendations = recommender.generate_recommendations(
            ranked_results,
            task_type=runner.task_type
        )

        recommender.display_recommendations()

        print("\n========== BENCHMARK FINISHED ==========")

        finish_progress()

        return {
            "dataset_id": runner.dataset_id,
            "dataset_name": runner.dataset_name,
            "task_type": runner.task_type,
            "results": results,
            "ranked_results": ranked_results,
            "recommendations": recommendations
        }

    except Exception as error:

        fail_progress(str(error))
        raise


# ============================================================
# 26. COMMAND-LINE EXECUTION
# ============================================================

if __name__ == "__main__":

    run_full_benchmark(
        dataset_id="breast_cancer",
        experiment_runs=5,
        inference_repeats=100
    )
