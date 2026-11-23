
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import numpy as np


def evaluate_classification(y_true, y_pred):
    """Calculate classification performance metrics."""

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                average="weighted",
                zero_division=0
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                average="weighted",
                zero_division=0
            )
        ),
        "f1_score": float(
            f1_score(
                y_true,
                y_pred,
                average="weighted",
                zero_division=0
            )
        )
    }


def evaluate_regression(y_true, y_pred):
    """Calculate regression performance metrics."""

    mse = mean_squared_error(y_true, y_pred)

    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mse),
        "rmse": float(np.sqrt(mse)),
        "r2_score": float(r2_score(y_true, y_pred))
    }


def evaluate_model(y_true, y_pred, task_type):
    """Select evaluation metrics according to the ML task."""

    if task_type == "classification":
        return evaluate_classification(y_true, y_pred)

    if task_type == "regression":
        return evaluate_regression(y_true, y_pred)

    raise ValueError(f"Unsupported task type: {task_type}")
