
from app.recommendation.eco_score import EcoScoreCalculator
from app.recommendation.model_recommender import ModelRecommender


calculator = EcoScoreCalculator()
recommender = ModelRecommender()


classification_results = [
    {
        "model_name": "Model A",
        "accuracy": 0.98,
        "energy_consumed_kwh": 0.00001,
        "inference_time_seconds": 0.001,
        "carbon_emissions_kg": 0.000002
    },
    {
        "model_name": "Model B",
        "accuracy": 0.90,
        "energy_consumed_kwh": 0.000005,
        "inference_time_seconds": 0.002,
        "carbon_emissions_kg": 0.000003
    }
]

regression_results = [
    {
        "model_name": "Regression A",
        "r2_score": 0.85,
        "energy_consumed_kwh": 0.00001,
        "inference_time_seconds": 0.001,
        "carbon_emissions_kg": 0.000002
    },
    {
        "model_name": "Regression B",
        "r2_score": -0.20,
        "energy_consumed_kwh": 0.000005,
        "inference_time_seconds": 0.002,
        "carbon_emissions_kg": 0.000003
    }
]


for task, results in [
    ("classification", classification_results),
    ("regression", regression_results)
]:

    print(f"\n========== {task.upper()} ==========")

    ranked = calculator.calculate_scores(
        results,
        task_type=task
    )

    for model in ranked:
        print(
            model["model_name"],
            "EcoScore:", model["eco_score"],
            "Eligible:", model["eligible"],
            "Reason:", model["eligibility_reason"]
        )

    recommendations = recommender.generate_recommendations(
        ranked,
        task_type=task
    )

    print("\nRECOMMENDATIONS")

    for key, value in recommendations.items():
        model = value["model"]

        print(
            key,
            "=>",
            model["model_name"] if model else "Unavailable"
        )
