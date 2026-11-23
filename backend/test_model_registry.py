
from app.benchmark.model_registry import get_models

for task in ["classification", "regression"]:

    print(f"\n{task.upper()} MODELS")

    models = get_models(task)

    for model_id, details in models.items():
        print(f"{model_id}: {details['name']}")

    print("Total models:", len(models))
