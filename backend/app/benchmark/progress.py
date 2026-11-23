
from threading import Lock
from datetime import datetime, timezone


_progress_lock = Lock()

_progress = {
    "status": "idle",
    "stage": "Not started",
    "current_model": None,
    "completed_models": 0,
    "total_models": 6,
    "completed_experiments": 0,
    "total_experiments": 30,
    "progress_percent": 0,
    "message": "No benchmark is currently running.",
    "started_at": None,
    "updated_at": None,
    "error": None
}


def start_progress(total_models=6, experiments_per_model=5):
    """Initialize progress when a new benchmark starts."""

    with _progress_lock:
        _progress.update({
            "status": "running",
            "stage": "Initializing",
            "current_model": None,
            "completed_models": 0,
            "total_models": total_models,
            "completed_experiments": 0,
            "total_experiments": total_models * experiments_per_model,
            "progress_percent": 0,
            "message": "Preparing benchmark execution.",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "error": None
        })


def update_model_progress(model_name, stage="Training"):
    """Update the model currently being evaluated."""

    with _progress_lock:
        _progress["current_model"] = model_name
        _progress["stage"] = stage
        _progress["message"] = f"{stage}: {model_name}"
        _progress["updated_at"] = datetime.now(timezone.utc).isoformat()


def complete_experiment(model_name=None):
    """Record completion of one experiment."""

    with _progress_lock:
        _progress["completed_experiments"] += 1

        total = _progress["total_experiments"]

        if total > 0:
            percentage = (
                _progress["completed_experiments"] / total
            ) * 100

            _progress["progress_percent"] = round(
                min(percentage, 100), 2
            )

        if model_name:
            _progress["current_model"] = model_name

        _progress["stage"] = "Experiment completed"
        _progress["message"] = (
            f"Completed {_progress['completed_experiments']} "
            f"of {_progress['total_experiments']} experiments."
        )

        _progress["updated_at"] = datetime.now(timezone.utc).isoformat()


def complete_model(model_name=None):
    """Record completion of a model's evaluation."""

    with _progress_lock:
        _progress["completed_models"] += 1
        _progress["stage"] = "Model completed"

        if model_name:
            _progress["current_model"] = model_name

        _progress["message"] = (
            f"Completed {_progress['completed_models']} "
            f"of {_progress['total_models']} models."
        )

        _progress["updated_at"] = datetime.now(timezone.utc).isoformat()


def finish_progress():
    """Mark the benchmark as successfully completed."""

    with _progress_lock:
        _progress["status"] = "completed"
        _progress["stage"] = "Completed"
        _progress["progress_percent"] = 100
        _progress["completed_experiments"] = (
            _progress["total_experiments"]
        )
        _progress["completed_models"] = _progress["total_models"]
        _progress["current_model"] = None
        _progress["message"] = "Benchmark completed successfully."
        _progress["updated_at"] = datetime.now(timezone.utc).isoformat()


def fail_progress(error_message):
    """Record a benchmark failure."""

    with _progress_lock:
        _progress["status"] = "failed"
        _progress["stage"] = "Failed"
        _progress["message"] = "Benchmark execution failed."
        _progress["error"] = str(error_message)
        _progress["updated_at"] = datetime.now(timezone.utc).isoformat()


def get_progress():
    """Return a safe copy of the current progress."""

    with _progress_lock:
        return _progress.copy()
