
import threading

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.database.operations import (
    get_benchmark_history,
    get_benchmark_details
)

from app.benchmark.runner import run_full_benchmark
from app.benchmark.progress import get_progress
from app.benchmark.dataset_loader import get_available_datasets


router = APIRouter(
    prefix="/api/benchmarks",
    tags=["Benchmarks"]
)

benchmark_lock = threading.Lock()

benchmark_state = {
    "status": "idle",
    "message": "No benchmark has been started.",
    "error": None
}


# Request structure for starting a benchmark
class BenchmarkRequest(BaseModel):

    dataset_id: str = "breast_cancer"

    experiment_runs: int = Field(
        default=5,
        ge=1,
        le=20
    )

    inference_repeats: int = Field(
        default=100,
        ge=1,
        le=1000
    )


def execute_benchmark(
    dataset_id: str,
    experiment_runs: int,
    inference_repeats: int
):

    try:

        benchmark_state["status"] = "running"
        benchmark_state["message"] = "Benchmark execution is in progress."
        benchmark_state["error"] = None

        run_full_benchmark(
            dataset_id=dataset_id,
            experiment_runs=experiment_runs,
            inference_repeats=inference_repeats
        )

        benchmark_state["status"] = "completed"
        benchmark_state["message"] = (
            "Benchmark completed and results were saved."
        )

    except Exception as error:

        benchmark_state["status"] = "failed"
        benchmark_state["message"] = "Benchmark execution failed."
        benchmark_state["error"] = str(error)

        print(f"Benchmark error: {error}")

    finally:

        benchmark_lock.release()


# --------------------------------------------------
# AVAILABLE DATASETS
# --------------------------------------------------

@router.get("/datasets")
def read_available_datasets():

    return {
        "datasets": get_available_datasets()
    }


# --------------------------------------------------
# BENCHMARK HISTORY
# --------------------------------------------------

@router.get("/")
def read_benchmark_history():

    try:

        return {
            "benchmarks": get_benchmark_history()
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# --------------------------------------------------
# BENCHMARK STATUS AND PROGRESS
# --------------------------------------------------

@router.get("/run/status")
def get_benchmark_status():

    progress = get_progress()

    return {
        **progress,
        "status": benchmark_state["status"],
        "message": benchmark_state["message"],
        "error": benchmark_state["error"]
    }


# --------------------------------------------------
# START BENCHMARK
# --------------------------------------------------

@router.post("/run", status_code=202)
def start_benchmark(
    request: BenchmarkRequest,
    background_tasks: BackgroundTasks
):

    available_datasets = {
        dataset["id"]
        for dataset in get_available_datasets()
    }

    if request.dataset_id not in available_datasets:

        raise HTTPException(
            status_code=400,
            detail="Invalid dataset selected."
        )

    if not benchmark_lock.acquire(blocking=False):

        raise HTTPException(
            status_code=409,
            detail="Another benchmark is already running."
        )

    benchmark_state["status"] = "queued"
    benchmark_state["message"] = "Benchmark has been queued."
    benchmark_state["error"] = None

    background_tasks.add_task(
        execute_benchmark,
        request.dataset_id,
        request.experiment_runs,
        request.inference_repeats
    )

    return {
        "message": "Benchmark execution started.",
        "status": "queued",
        "dataset_id": request.dataset_id,
        "experiment_runs": request.experiment_runs,
        "inference_repeats": request.inference_repeats,
        "status_endpoint": "/api/benchmarks/run/status"
    }


# --------------------------------------------------
# BENCHMARK DETAILS
# --------------------------------------------------

@router.get("/{benchmark_id}")
def read_benchmark_details(benchmark_id: int):

    try:

        benchmark = get_benchmark_details(benchmark_id)

        if not benchmark:

            raise HTTPException(
                status_code=404,
                detail="Benchmark not found."
            )

        return benchmark

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
