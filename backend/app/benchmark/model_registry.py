
from sklearn.linear_model import (
    LogisticRegression,
    LinearRegression,
    Ridge
)

from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    RandomForestRegressor,
    GradientBoostingRegressor
)

from sklearn.svm import SVC, SVR

from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor


CLASSIFICATION_MODELS = {
    "logistic_regression": {
        "name": "Logistic Regression",
        "model": LogisticRegression(max_iter=2000)
    },

    "decision_tree": {
        "name": "Decision Tree",
        "model": DecisionTreeClassifier(random_state=42)
    },

    "random_forest": {
        "name": "Random Forest",
        "model": RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
    },

    "svm": {
        "name": "Support Vector Machine",
        "model": SVC()
    },

    "knn": {
        "name": "K-Nearest Neighbors",
        "model": KNeighborsClassifier()
    },

    "gradient_boosting": {
        "name": "Gradient Boosting",
        "model": GradientBoostingClassifier(random_state=42)
    }
}


REGRESSION_MODELS = {
    "linear_regression": {
        "name": "Linear Regression",
        "model": LinearRegression()
    },

    "ridge": {
        "name": "Ridge Regression",
        "model": Ridge()
    },

    "decision_tree": {
        "name": "Decision Tree Regressor",
        "model": DecisionTreeRegressor(random_state=42)
    },

    "random_forest": {
        "name": "Random Forest Regressor",
        "model": RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
    },

    "svr": {
        "name": "Support Vector Regressor",
        "model": SVR()
    },

    "gradient_boosting": {
        "name": "Gradient Boosting Regressor",
        "model": GradientBoostingRegressor(random_state=42)
    }
}


def get_models(task_type):
    """Return models compatible with the selected task."""

    if task_type == "classification":
        return CLASSIFICATION_MODELS

    if task_type == "regression":
        return REGRESSION_MODELS

    raise ValueError(f"Unsupported task type: {task_type}")
