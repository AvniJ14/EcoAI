
from sklearn.datasets import (
    load_breast_cancer,
    load_iris,
    load_digits,
    load_wine,
    load_diabetes,
    fetch_california_housing
)

from sklearn.model_selection import train_test_split


DATASET_REGISTRY = {
    "breast_cancer": {
        "name": "Breast Cancer Wisconsin",
        "task": "classification",
        "loader": load_breast_cancer
    },
    "iris": {
        "name": "Iris",
        "task": "classification",
        "loader": load_iris
    },
    "digits": {
        "name": "Digits",
        "task": "classification",
        "loader": load_digits
    },
    "wine": {
        "name": "Wine",
        "task": "classification",
        "loader": load_wine
    },
    "diabetes": {
        "name": "Diabetes",
        "task": "regression",
        "loader": load_diabetes
    },
    "california_housing": {
        "name": "California Housing",
        "task": "regression",
        "loader": fetch_california_housing
    }
}


def get_available_datasets():
    """Return information about all supported datasets."""

    return [
        {
            "id": dataset_id,
            "name": details["name"],
            "task": details["task"]
        }
        for dataset_id, details in DATASET_REGISTRY.items()
    ]


def load_dataset(dataset_id, test_size=0.2, random_state=42):
    """
    Load a dataset and split it into training and testing sets.

    Supports classification and regression datasets.
    """

    if dataset_id not in DATASET_REGISTRY:
        raise ValueError(
            f"Unknown dataset: {dataset_id}. "
            f"Available datasets: {list(DATASET_REGISTRY.keys())}"
        )

    details = DATASET_REGISTRY[dataset_id]

    # Load dataset
    dataset = details["loader"]()

    X = dataset.data
    y = dataset.target

    task_type = details["task"]

    # Stratification is used only for classification
    stratify = y if task_type == "classification" else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify
    )

    return {
        "dataset_id": dataset_id,
        "dataset_name": details["name"],
        "task_type": task_type,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "total_samples": len(X),
        "training_samples": len(X_train),
        "testing_samples": len(X_test),
        "total_features": X.shape[1],
        "feature_names": list(dataset.feature_names),
        "target_names": (
            list(dataset.target_names)
            if hasattr(dataset, "target_names")
            else None
        )
    }
