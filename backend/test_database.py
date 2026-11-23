
from app.database.operations import (
    get_benchmark_history,
    get_benchmark_details
)


print("\n========== BENCHMARK HISTORY ==========")

history = get_benchmark_history()

for benchmark in history:

    print(f"\nBenchmark ID: {benchmark['id']}")
    print(f"Dataset: {benchmark['dataset_name']}")
    print(f"Models: {benchmark['total_models']}")
    print(f"Status: {benchmark['status']}")


print("\n========== BENCHMARK DETAILS ==========")

details = get_benchmark_details(1)

if details:

    print(f"Benchmark ID: {details['id']}")

    for model in details["models"]:

        print("\n-----------------------------")
        print(f"Model: {model['model_name']}")
        print(f"Accuracy: {model['accuracy']}")
        print(f"EcoScore: {model['eco_score']}")
        print(
            f"Experiments: {len(model['experiments'])}"
        )

else:

    print("Benchmark not found.")
