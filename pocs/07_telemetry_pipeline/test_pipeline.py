import unittest

from pipeline import (Destination, Pipeline, Reducer, Route, enricher, normalize, secure, stable_hash,
                      tier_for)


class StageTests(unittest.TestCase):
    def test_normalize_plaintext_log(self):
        ev = normalize("2026-01-01T00:00:00Z ERROR payment failed order_id=42 user.email=a@b.com")
        self.assertEqual(ev["severity"], "error")
        self.assertEqual(ev["order_id"], 42)
        self.assertEqual(ev["user.email"], "a@b.com")

    def test_secure_hashes_ids_and_redacts_free_text(self):
        ev = secure({"user.email": "a@b.com", "body": "card 4111 1111 1111 1111 for x@y.io"})
        self.assertEqual(ev["user.email"], stable_hash("a@b.com"))
        self.assertNotIn("4111", ev["body"])
        self.assertNotIn("x@y.io", ev["body"])

    def test_allowlist(self):
        self.assertEqual(secure({"a": 1, "secret": 2}, allow={"a"}), {"a": 1})

    def test_enrich_and_reduce(self):
        e = enricher({"k8s.cluster.name": "prod-1"}, {"tier": lambda ev: "high"})({"body": "x"})
        self.assertEqual((e["k8s.cluster.name"], e["tier"]), ("prod-1", "high"))
        r = Reducer(drop=lambda ev: ev.get("http.route") == "/healthz", drop_fields=("pod.uid",))
        self.assertIsNone(r({"http.route": "/healthz"}))
        self.assertNotIn("pod.uid", r({"severity": "error", "pod.uid": "x"}))
        self.assertIsNotNone(r({"severity": "info", "body": "hello"}))
        self.assertIsNone(r({"severity": "info", "body": "hello"}))  # duplicate collapsed


class RoutingTests(unittest.TestCase):
    def test_fan_out_and_backpressure(self):
        siem, apm, archive = [], [], []
        d_siem = Destination("siem", siem.extend, capacity=2)
        d_apm = Destination("apm", apm.extend)
        d_arc = Destination("archive", archive.extend)
        p = Pipeline([secure, Reducer()], [
            Route(lambda e: e.get("category") == "security", d_siem),
            Route(lambda e: "duration_ms" in e, d_apm),
            Route(lambda e: True, d_arc),
        ])
        for i in range(3):
            p.process({"category": "security", "body": f"login {i}", "severity": "warn"})
        p.process({"duration_ms": 12, "body": "req"})
        for d in (d_siem, d_apm, d_arc):
            d.flush()
        self.assertEqual(len(siem), 2)
        self.assertEqual(p.stats["backpressure"], 1)
        self.assertEqual(len(apm), 1)
        self.assertEqual(len(archive), 4)

    def test_retry_with_backoff_then_success(self):
        attempts = {"n": 0}
        got = []

        def flaky(batch):
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise ConnectionError
            got.extend(batch)

        d = Destination("vendor", flaky, base_delay=0.1)
        d.offer({"x": 1})
        self.assertEqual(d.flush(), 1)
        self.assertEqual(len(d.slept), 2)
        self.assertTrue(all(0 <= s <= 0.1 * 2 ** i for i, s in enumerate(d.slept)))

    def test_data_kept_when_backend_down(self):
        def down(batch):
            raise ConnectionError
        d = Destination("vendor", down, max_retries=2)
        d.offer({"x": 1})
        self.assertEqual(d.flush(), 0)
        self.assertEqual(len(d.queue), 1)


class TierTests(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(tier_for({"revenue": True}), "high")
        self.assertEqual(tier_for({"customer_facing": True}), "medium")
        self.assertEqual(tier_for({}), "low")


if __name__ == "__main__":
    unittest.main()
