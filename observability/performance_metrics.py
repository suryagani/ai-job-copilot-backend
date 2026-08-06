from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from statistics import mean
from time import time


@dataclass
class PerformanceRegistry:
    latencies: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    failures: list[dict] = field(default_factory=list)

    def record_latency(self, endpoint: str, duration_ms: float) -> None:
        self.latencies[endpoint].append(float(duration_ms))

    def increment(self, key: str, amount: int = 1) -> None:
        self.counters[key] += int(amount)

    def record_failure(self, endpoint: str, category: str, detail: str = "") -> None:
        self.failures.append(
            {
                "endpoint": endpoint,
                "category": category,
                "detail": str(detail or "")[:240],
                "timestamp": time(),
            }
        )
        self.failures = self.failures[-200:]

    def latency_summary(self) -> dict:
        summary = {}
        for endpoint, values in self.latencies.items():
            ordered = sorted(values)
            count = len(ordered)
            p50_index = max(0, min(count - 1, int(count * 0.5) - 1))
            p95_index = max(0, min(count - 1, int(count * 0.95) - 1))
            summary[endpoint] = {
                "count": count,
                "average_ms": round(mean(ordered), 2) if ordered else 0,
                "p50_ms": round(ordered[p50_index], 2) if ordered else 0,
                "p95_ms": round(ordered[p95_index], 2) if ordered else 0,
                "max_ms": round(max(ordered), 2) if ordered else 0,
            }
        return summary


metrics_registry = PerformanceRegistry()
