
from app.benchmark.dataset_loader import (
    get_available_datasets,
    load_dataset
)

print("\nAVAILABLE DATASETS")

for dataset in get_available_datasets():
    print(dataset)

print("\nTESTING DATASET LOADING")

for dataset_id in [
    "breast_cancer",
    "iris",
    "digits",
    "wine",
    "diabetes",
    "california_housing"
]:

    data = load_dataset(dataset_id)

    print("\nDataset:", data["dataset_name"])
    print("Task:", data["task_type"])
    print("Total samples:", data["total_samples"])
    print("Training samples:", data["training_samples"])
    print("Testing samples:", data["testing_samples"])
    print("Features:", data["total_features"])
