
from app.benchmark.evaluation import evaluate_model

# Classification test
y_true_class = [0, 1, 1, 0, 1]
y_pred_class = [0, 1, 0, 0, 1]

print("\nCLASSIFICATION RESULTS")
print(
    evaluate_model(
        y_true_class,
        y_pred_class,
        "classification"
    )
)

# Regression test
y_true_reg = [10, 20, 30, 40, 50]
y_pred_reg = [12, 18, 29, 42, 48]

print("\nREGRESSION RESULTS")
print(
    evaluate_model(
        y_true_reg,
        y_pred_reg,
        "regression"
    )
)
