import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_wide_events"))
from bubbleup import bubble_up, core_analysis_loop  # noqa: E402
from wide_events import synthetic_checkout_events  # noqa: E402


def az_incident(n=4000, seed=1):
    """Recreates the ch8 story: one AZ (us-east-1a) on one instance type goes slow."""
    rng = random.Random(seed)
    evs = []
    for _ in range(n):
        az = rng.choice(["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1f", "us-east-1e"])
        itype = rng.choice(["m6i.xlarge", "c7g.large"])
        dur = rng.gauss(80, 10)
        if az == "us-east-1a" and itype == "m6i.xlarge":
            dur += 900
        evs.append({"global.availability_zone": az, "instance.type": itype, "duration_ms": dur,
                    "user.id": f"u{rng.randint(0, 5000)}", "http.route": rng.choice(["/a", "/b"])})
    return evs


class BubbleUpTests(unittest.TestCase):
    def test_finds_the_availability_zone(self):
        top = bubble_up(az_incident(), lambda e: e["duration_ms"] > 500)
        self.assertEqual((top[0]["field"], top[0]["value"]), ("global.availability_zone", "us-east-1a"))
        self.assertGreater(top[0]["selection_pct"], 95)
        self.assertLess(top[0]["baseline_pct"], 20)

    def test_high_cardinality_ids_are_skipped(self):
        fields = {f["field"] for f in bubble_up(az_incident(), lambda e: e["duration_ms"] > 500, top=50)}
        self.assertNotIn("user.id", fields)

    def test_core_analysis_loop_narrows_to_multicausal_cohort(self):
        evs = synthetic_checkout_events()
        found = core_analysis_loop(evs, lambda e: e["duration_ms"] > 250)
        pairs = {(f["field"], f["value"]) for f in found}
        self.assertIn(("deploy.build_id", "b_4471"), pairs)
        self.assertIn(("cloud.region", "ap-southeast-2"), pairs)
        self.assertIn(("feature_flag.new_checkout", "True"), pairs)

    def test_empty_selection(self):
        self.assertEqual(bubble_up([{"a": 1}], lambda e: False), [])


if __name__ == "__main__":
    unittest.main()
