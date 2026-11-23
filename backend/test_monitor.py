
import time
from app.monitoring.resource_monitor import ResourceMonitor

monitor = ResourceMonitor()

print("Starting resource monitoring...")

monitor.start_monitoring()

# Simulate a small task
total = 0
for i in range(10_000_000):
    total += i

time.sleep(1)

results = monitor.stop_monitoring()

print("\nResource Monitoring Results")
print("---------------------------")

for metric, value in results.items():
    print(f"{metric}: {value}")
