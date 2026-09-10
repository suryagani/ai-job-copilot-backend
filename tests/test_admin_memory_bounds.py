import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import analytics_engine
import auth_cloud_sync
from observability.performance_metrics import PerformanceRegistry


class _Response:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class AdminMemoryBoundsTests(unittest.TestCase):
    def test_waitlist_query_has_hard_maximum(self):
        captured = {}

        def request(method, path, **kwargs):
            captured.update(kwargs)
            return _Response([])

        with patch.object(auth_cloud_sync, "_admin_rest_request", side_effect=request):
            result = auth_cloud_sync.list_waitlist_entries(limit=10000)

        self.assertEqual(result, [])
        self.assertEqual(captured["params"]["limit"], "100")

    def test_user_and_asset_queries_are_bounded(self):
        captured = []
        profiles = [{"id": "user-1", "role": "user", "account_status": "active"}]

        def request(method, path, **kwargs):
            captured.append((path, kwargs["params"]))
            return _Response(profiles if path.endswith("/profiles") else [])

        with patch.object(auth_cloud_sync, "_admin_rest_request", side_effect=request):
            result = auth_cloud_sync.list_admin_users(limit=10000)

        self.assertEqual(len(result), 1)
        self.assertEqual(captured[0][1]["limit"], "100")
        self.assertEqual(captured[1][1]["limit"], "5000")

    def test_analytics_snapshot_is_bounded_and_shared(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.json"
            events = [{"id": str(index), "created_at": str(index)} for index in range(5)]
            path.write_text(json.dumps(events), encoding="utf-8")
            with patch.object(analytics_engine, "ANALYTICS_FILE", path), patch.object(
                analytics_engine, "ANALYTICS_MAX_EVENTS", 2
            ):
                with analytics_engine._ANALYTICS_CACHE_LOCK:
                    analytics_engine._ANALYTICS_CACHE = ()
                    analytics_engine._ANALYTICS_CACHE_LOADED_AT = 0
                first = analytics_engine.list_analytics_events()
                second = analytics_engine.list_analytics_events()

        self.assertEqual(len(first), 2)
        self.assertIs(first, second)

    def test_latency_samples_are_bounded(self):
        registry = PerformanceRegistry()
        for value in range(1500):
            registry.record_latency("/admin/test", value)
        self.assertLessEqual(len(registry.latencies["/admin/test"]), 1000)


if __name__ == "__main__":
    unittest.main()
