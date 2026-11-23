
import math


class ModelRecommender:
    """
    Generates metric-based recommendations for
    classification and regression models.
    """

    def __init__(self):
        self.recommendations = {}
        self.task_type = "classification"

    @staticmethod
    def _valid_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )

    def _best_model(self, models, metric, reverse=False):

        valid_models = [
            model for model in models
            if self._valid_number(model.get(metric))
        ]

        if not valid_models:
            return None

        return sorted(
            valid_models,
            key=lambda model: model[metric],
            reverse=reverse
        )[0]

    def generate_recommendations(
        self,
        ranked_results,
        task_type="classification"
    ):

        if task_type not in ("classification", "regression"):
            raise ValueError(
                f"Unsupported task type: {task_type}"
            )

        self.task_type = task_type

        quality_metric = (
            "accuracy"
            if task_type == "classification"
            else "r2_score"
        )

        quality_label = (
            "accuracy"
            if task_type == "classification"
            else "R2 score"
        )

        best_accuracy = self._best_model(
            ranked_results,
            quality_metric,
            reverse=True
        )

        lowest_energy = self._best_model(
            ranked_results,
            "energy_consumed_kwh"
        )

        fastest_inference = self._best_model(
            ranked_results,
            "inference_time_seconds"
        )

        lowest_carbon = self._best_model(
            ranked_results,
            "carbon_emissions_kg"
        )

        eligible_models = [
            model for model in ranked_results
            if model.get("eligible") is True
            and model.get("eco_score") is not None
        ]

        best_balanced = self._best_model(
            eligible_models,
            "eco_score",
            reverse=True
        )

        self.recommendations = {

            "best_accuracy": {
                "model": best_accuracy,
                "explanation": (
                    f"Achieved the highest predictive "
                    f"{quality_label}."
                )
            },

            "lowest_energy": {
                "model": lowest_energy,
                "explanation": (
                    "Consumed the least estimated energy "
                    "among the evaluated models."
                )
            },

            "fastest_inference": {
                "model": fastest_inference,
                "explanation": (
                    "Required the least average time to "
                    "complete an inference operation."
                )
            },

            "lowest_carbon": {
                "model": lowest_carbon,
                "explanation": (
                    "Produced the lowest estimated carbon "
                    "emissions during benchmarking."
                )
            },

            "best_balanced": {
                "model": best_balanced,
                "explanation": (
                    f"Achieved the highest EcoScore while "
                    f"meeting the minimum {quality_label} "
                    f"requirement."
                )
            }
        }

        return self.recommendations

    def display_recommendations(self):

        quality_label = (
            "Accuracy"
            if self.task_type == "classification"
            else "R2 Score"
        )

        quality_metric = (
            "accuracy"
            if self.task_type == "classification"
            else "r2_score"
        )

        labels = {
            "best_accuracy": (
                "BEST ACCURACY"
                if self.task_type == "classification"
                else "BEST R2 SCORE"
            ),
            "lowest_energy": "LOWEST ENERGY CONSUMPTION",
            "fastest_inference": "FASTEST INFERENCE",
            "lowest_carbon": "LOWEST CARBON EMISSIONS",
            "best_balanced": "BEST BALANCED MODEL"
        }

        print("\n========== MODEL RECOMMENDATIONS ==========")

        for key, label in labels.items():

            recommendation = self.recommendations.get(key)

            print(f"\n---------- {label} ----------")

            if not recommendation:
                print("No recommendation available.")
                continue

            model = recommendation["model"]

            if model is None:
                print("No suitable model available.")
                continue

            print(
                f"Model: {model.get('model_name', 'Unknown')}"
            )

            quality = model.get(quality_metric)

            if self._valid_number(quality):
                print(
                    f"{quality_label}: {quality:.4f}"
                )
            else:
                print(f"{quality_label}: Not available")

            print(
                f"Explanation: {recommendation['explanation']}"
            )

            if key == "lowest_energy":
                print(
                    f"Energy: {model.get('energy_consumed_kwh')} kWh"
                )

            elif key == "fastest_inference":
                print(
                    f"Inference: "
                    f"{model.get('inference_time_seconds')} seconds"
                )

            elif key == "lowest_carbon":
                print(
                    f"Carbon: "
                    f"{model.get('carbon_emissions_kg')} kg"
                )

            elif key == "best_balanced":
                print(
                    f"EcoScore: {model.get('eco_score')}"
                )
