
import psutil
import os
import time


class ResourceMonitor:

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = None
        self.start_memory = None

    def start_monitoring(self):
        """Start CPU, memory and time monitoring."""

        self.start_time = time.perf_counter()

        self.start_memory = (
            self.process.memory_info().rss / (1024 * 1024)
        )

        # Prime CPU measurement before the workload
        self.process.cpu_percent(interval=None)

    def stop_monitoring(self):
        """Collect resource measurements after execution."""

        if self.start_time is None:
            raise RuntimeError("Monitoring has not been started.")

        elapsed_time = time.perf_counter() - self.start_time

        cpu_usage = self.process.cpu_percent(interval=None)

        end_memory = (
            self.process.memory_info().rss / (1024 * 1024)
        )

        memory_change = end_memory - self.start_memory

        results = {
            "inference_time_seconds": round(elapsed_time, 6),
            "cpu_usage_percent": round(cpu_usage, 2),
            "memory_before_mb": round(self.start_memory, 2),
            "memory_after_mb": round(end_memory, 2),
            "memory_change_mb": round(memory_change, 2)
        }

        self.start_time = None
        return results
