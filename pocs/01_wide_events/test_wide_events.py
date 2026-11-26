import unittest

from wide_events import (WideEvent, aggregate, naive_avg_of_avgs, narrative, percentile,
                         synthetic_checkout_events, time_buckets, weighted_avg)


class WideEventTests(unittest.TestCase):
    def test_emits_one_flat_event_with_context_and_timings(self):
        sink = []
        ev = WideEvent("checkout", sink).add(**{"user.id": "u1", "cart.items": 3})
        with ev.time_block("db.query"):
            sum(range(1000))
        out = ev.finish()
        self.assertEqual(len(sink), 1)
        self.assertTrue(out["main"])
        self.assertIn("db.query.duration_ms", out)
        self.assertEqual(out["user.id"], "u1")
        self.assertFalse(out["error"])

    def test_error_fields_and_slug(self):
        sink = []
        out = WideEvent("charge", sink).finish(ValueError("card declined"), slug="err-stripe-declined")
        self.assertTrue(out["error"])
        self.assertEqual(out["exception.slug"], "err-stripe-declined")
        self.assertEqual(out["exception.type"], "ValueError")

    def test_percentile_nearest_rank(self):
        self.assertEqual(percentile(list(range(1, 101)), 99), 99)
        self.assertEqual(percentile([5], 50), 5)

    def test_slicing_finds_the_slow_cohort(self):
        evs = synthetic_checkout_events()
        by = aggregate(evs, ("deploy.build_id", "feature_flag.new_checkout", "cloud.region"), "duration_ms", "p99")
        worst = max(by, key=by.get)
        self.assertEqual(worst, ("b_4471", True, "ap-southeast-2"))

    def test_new_dimension_without_schema_change(self):
        evs = synthetic_checkout_events(500)
        self.assertEqual(set(k[0] for k in aggregate(evs, ("user.plan",), "duration_ms", "count")),
                         {"free", "pro", "enterprise"})

    def test_derive_metric_series_and_narrative(self):
        evs = synthetic_checkout_events(240)
        series = time_buckets(evs, 60, "duration_ms", "count")
        self.assertEqual(sum(series.values()), 240)
        self.assertEqual(len(narrative(evs[:3], "ts", "user.id")), 3)

    def test_average_of_averages_trap(self):
        self.assertAlmostEqual(naive_avg_of_avgs({"a": 120, "b": 230, "c": 200}), 183.33, places=2)
        correct = weighted_avg({"a": 100, "b": 57, "c": 98}, {"a": 12000, "b": 13110, "c": 19600})
        self.assertAlmostEqual(correct, 175.33, places=2)


if __name__ == "__main__":
    unittest.main()
