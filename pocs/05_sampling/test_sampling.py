import random
import unittest

from sampling import (FixedRateSampler, KeyedTargetRateSampler, keep_consistent, tail_sample,
                      weighted_count, weighted_percentile, weighted_sum)


class Reconstruction(unittest.TestCase):
    def test_book_weighted_median(self):
        pairs = [(1, 5), (3, 2), (7, 9)]
        self.assertEqual(sorted(v for v, _ in pairs)[1], 3)  # naive
        self.assertEqual(weighted_percentile(pairs, 50), 7)  # correct

    def test_fixed_rate_reconstructs_count(self):
        s = FixedRateSampler(100, random.Random(3))
        kept = [k for k in (s.sample({"i": i, "duration_ms": 10}) for i in range(100_000)) if k]
        est = weighted_count(kept)
        self.assertLess(abs(est - 100_000) / 100_000, 0.1)
        self.assertAlmostEqual(weighted_sum(kept, "duration_ms") / est, 10)

    def test_head_sampling_misses_rare_errors(self):
        rng = random.Random(9)
        events = [{"error": rng.random() < 0.001} for _ in range(5_000)]  # ~5 errors
        kept = [k for k in (FixedRateSampler(100, random.Random(1)).sample(e) for e in events) if k]
        self.assertLessEqual(sum(e["error"] for e in kept), 1)  # most likely 0


class Consistency(unittest.TestCase):
    def test_all_services_agree(self):
        ids = [f"{i:032x}" for i in range(2000)]
        a = [keep_consistent(t, 10) for t in ids]
        b = [keep_consistent(t, 10) for t in ids]
        self.assertEqual(a, b)
        self.assertAlmostEqual(sum(a) / len(a), 0.1, delta=0.03)

    def test_child_with_higher_rate_never_orphaned(self):
        # parent kept at 1/10, noisy redis child at 1/1000: child kept => parent kept
        for i in range(20_000):
            t = f"{i:032x}"
            if keep_consistent(t, 1000):
                self.assertTrue(keep_consistent(t, 10))


class KeyedSampler(unittest.TestCase):
    def test_rare_keys_kept_noisy_keys_squeezed(self):
        s = KeyedTargetRateSampler(lambda e: (e["status"],), target_per_interval=100,
                                   never=lambda e: e.get("path") == "/healthz", rng=random.Random(2))
        traffic = [{"status": 200}] * 9_900 + [{"status": 500}] * 100 + [{"status": 200, "path": "/healthz"}] * 50
        for e in traffic:
            s.sample(e)
        s.rollover()
        kept = [k for k in (s.sample(e) for e in traffic) if k]
        errors = [k for k in kept if k["status"] == 500]
        oks = [k for k in kept if k["status"] == 200]
        # fair share is 50 per key: errors kept at ~1/2, successes at ~1/198
        self.assertGreater(len(errors) / 100, 50 * len(oks) / 9_900)
        self.assertAlmostEqual(weighted_count(kept, lambda e: e["status"] == 500), 100, delta=30)
        self.assertTrue(all(k.get("path") != "/healthz" for k in kept))
        self.assertAlmostEqual(weighted_count(kept, lambda e: e["status"] == 200), 9_900, delta=1_500)

    def test_tail_sampling_keeps_errors_and_slow(self):
        ok = [{"trace.trace_id": "f" * 32, "trace.parent_id": None, "duration_ms": 40}]
        err = [{"trace.trace_id": "e" * 32, "trace.parent_id": None, "duration_ms": 40},
               {"trace.trace_id": "e" * 32, "trace.parent_id": "x", "duration_ms": 5, "error": True}]
        slow = [{"trace.trace_id": "d" * 32, "trace.parent_id": None, "duration_ms": 900}]
        self.assertEqual(tail_sample(err, 100), (True, 1))
        self.assertEqual(tail_sample(slow, 100), (True, 1))
        self.assertEqual(tail_sample(ok, 100)[1], 100)


if __name__ == "__main__":
    unittest.main()
