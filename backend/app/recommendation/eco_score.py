
import math


class EcoScoreCalculator:
    """
    Calculates task-aware EcoScores for classification
    and regression models.
    """

    def __init__(
        self,
        accuracy_weight=0.60,
        energy_weight=0.40,
        min_accuracy=95,
        min_r2=0.70
    ):

        self.accuracy_weight = accuracy_weight
        self.energy_weight = energy_weight
        self.min_accuracy = min_accuracy
        self.min_r2 = min_r2

        if accuracy_weight < 0 or energy_weight < 0:
            raise ValueError("Scoring weights cannot be negative.")

        if round(accuracy_weight + energy_weight, 8) != 1:
            raise ValueError("Scoring weights must add up to 1.")

        if not 0 <= min_accuracy <= 100:
            raise ValueError(
                "Minimum accuracy must be between 0 and 100."
            )

        if not -1 <= min_r2 <= 1:
            raise ValueError(
                "Minimum R2 must be between -1 and 1."
            )

    @staticmethod
    def _valid_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )

    def _get_quality_score(self, result, task_type):
        """Return predictive quality as a percentage."""

        if task_type == "classification":

            accuracy = result.get("accuracy")

            if not self._valid_number(accuracy):
                return None

            return accuracy * 100 if accuracy <= 1 else accuracy

        if task_type == "regression":

            r2 = result.get("r2_score")

            if not self._valid_number(r2):
                return None

            # R2 is converted to a percentage-like score.
            # Negative R2 values remain negative.
            return r2 * 100

        raise ValueError(f"Unsupported task type: {task_type}")

    def is_eligible(self, quality_score, task_type):
        """Check whether a model meets the quality threshold."""

        if not self._valid_number(quality_score):
            return False

        if task_type == "classification":
            return quality_score >= self.min_accuracy

        if task_type == "regression":
            return quality_score >= self.min_r2 * 100

        return False

    def calculate_scores(
        self,
        results,
        task_type="classification"
    ):
        """Calculate EcoScores and rank benchmark results."""

        if not results:
            return []

        if task_type not in ("classification", "regression"):
            raise ValueError(f"Unsupported task type: {task_type}")

        eligible_models = []
        ineligible_models = []

        # Separate eligible and ineligible models.
        for result in results:

            model = result.copy()

            quality_score = self._get_quality_score(
                model,
                task_type
            )

            energy = model.get("energy_consumed_kwh")

            valid_energy = (
                self._valid_number(energy)
                and energy > 0
            )

            model["task_type"] = task_type
            model["quality_score"] = (
                round(quality_score, 2)
                if quality_score is not None
                else None
            )

            if (
                self.is_eligible(quality_score, task_type)
                and valid_energy
            ):
                eligible_models.append(model)

            else:
                ineligible_models.append(model)

        # Calculate energy efficiency among eligible models.
        if eligible_models:

            minimum_energy = min(
                model["energy_consumed_kwh"]
                for model in eligible_models
            )

            for model in eligible_models:

                quality_score = model["quality_score"]
                energy = model["energy_consumed_kwh"]

                energy_efficiency = (
                    minimum_energy / energy
                ) * 100

                eco_score = (
                    self.accuracy_weight * quality_score
                    + self.energy_weight * energy_efficiency
                )

                model["energy_efficiency_score"] = round(
                    energy_efficiency, 2
                )

                model["eco_score"] = round(eco_score, 2)
                model["eligible"] = True
                model["recommendation_status"] = "Eligible"

                model["eligibility_reason"] = (
                    "Meets the minimum predictive quality "
                    "and energy measurement requirements."
                )

                if task_type == "classification":
                    model["accuracy_percentage"] = round(
                        quality_score, 2
                    )
                else:
                    model["r2_percentage"] = round(
                        quality_score, 2
                    )

            eligible_models.sort(
                key=lambda model: model["eco_score"],
                reverse=True
            )

            for rank, model in enumerate(
                eligible_models,
                start=1
            ):
                model["rank"] = rank

        # Keep ineligible models visible.
        for model in ineligible_models:

            quality_score = model.get("quality_score")
            energy = model.get("energy_consumed_kwh")

            model["eco_score"] = None
            model["energy_efficiency_score"] = None
            model["eligible"] = False
            model["rank"] = None

            if quality_score is not None:

                if task_type == "classification":
                    model["accuracy_percentage"] = round(
                        quality_score, 2
                    )
                else:
                    model["r2_percentage"] = round(
                        quality_score, 2
                    )

            if not self.is_eligible(
                quality_score,
                task_type
            ):

                model["recommendation_status"] = "Not Eligible"

                if task_type == "classification":
                    reason = (
                        f"Accuracy is below the minimum "
                        f"requirement of {self.min_accuracy}%."
                    )
                else:
                    reason = (
                        f"R2 score is below the minimum "
                        f"requirement of {self.min_r2}."
                    )

                model["eligibility_reason"] = reason

            elif not (
                self._valid_number(energy) and energy > 0
            ):

                model["recommendation_status"] = "Not Scored"

                model["eligibility_reason"] = (
                    "A valid positive energy measurement "
                    "is unavailable."
                )

        return eligible_models + ineligible_models
