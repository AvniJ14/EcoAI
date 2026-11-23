
from codecarbon import EmissionsTracker


class EnergyMonitor:

    def __init__(self, project_name="EcoAI Benchmark"):
        self.tracker = EmissionsTracker(
            project_name=project_name,
            measure_power_secs=1,
            tracking_mode="process",
            log_level="error",
            allow_multiple_runs=False
        )

        self.is_running = False

    def start_monitoring(self):
        """Start the single benchmark tracking session."""

        if self.is_running:
            raise RuntimeError("Energy monitoring is already running.")

        self.tracker.start()
        self.is_running = True

    def start_task(self, task_name):
        """Start tracking one model's workload."""

        if not self.is_running:
            raise RuntimeError("Start the main tracker first.")

        self.tracker.start_task(task_name=task_name)

    def stop_task(self, task_name):
        """Stop a model task and retrieve its measurements."""

        task_data = self.tracker.stop_task(task_name=task_name)

        energy = getattr(task_data, "energy_consumed", None)
        emissions = getattr(task_data, "emissions", None)
        duration = getattr(task_data, "duration", None)

        return {
            "energy_consumed_kwh": (
                round(energy, 10) if energy is not None else None
            ),
            "carbon_emissions_kg": (
                round(emissions, 10) if emissions is not None else None
            ),
            "energy_tracking_duration_seconds": (
                round(duration, 4) if duration is not None else None
            )
        }

    def stop_monitoring(self):
        """Stop the complete benchmark tracking session."""

        if not self.is_running:
            return None

        total_emissions = self.tracker.stop()
        self.is_running = False

        return total_emissions
