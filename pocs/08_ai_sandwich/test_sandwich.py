import unittest

from sandwich import (IntervalSeries, InvariantViolation, Tariff, Window, cost_at_query_time, price,
                      promote_to_eval, rejection_rate, repair_query, validate_plan)

TOU = Tariff("tariff-55", "2025.12.1", (Window(7, 22, 0.40), Window(22, 7, 0.10)))  # wraps midnight
USAGE = IntervalSeries("home-1234", tuple([1.0] * 18 + [10.0] + [1.0] * 5))  # 10 kWh EV charge at 18:00


class DeterministicCore(unittest.TestCase):
    def test_price_and_determinism(self):
        a, b = price(USAGE, TOU), price(USAGE, TOU)
        self.assertEqual(a["determinism_hash"], b["determinism_hash"])
        self.assertEqual(a["applied_tariff_id"], "tariff-55")
        self.assertAlmostEqual(a["total_cost"], 9 * 0.10 + 6 * 0.40 + 0.40 * 10 + 8 * 0.40, places=2)

    def test_coverage_gap_detected(self):
        gap = Tariff("broken", "x", (Window(7, 20, 0.4), Window(22, 7, 0.1)))  # 20-22 uncovered
        with self.assertRaises(InvariantViolation) as cm:
            price(USAGE, gap)
        self.assertEqual(cm.exception.invariant, "coverage")

    def test_overlap_detected(self):
        overlap = Tariff("dup", "x", (Window(0, 24, 0.4), Window(22, 7, 0.1)))
        with self.assertRaises(InvariantViolation):
            price(USAGE, overlap)


class Sandwich(unittest.TestCase):
    def plan(self, predicted, frm=18, to=23, kwh=10, conf=0.9, pid="p1"):
        return {"plan_id": pid, "predicted": {"bill_delta_usd": predicted}, "confidence": conf,
                "model_name": "model-a", "prompt_version": "v7",
                "actions": [{"device": "ev_charging", "from_h": frm, "to_h": to, "kwh": kwh}]}

    def test_honest_plan_accepted(self):
        ev = validate_plan(USAGE, TOU, self.plan(-3.0))
        self.assertEqual(ev["proposal_status"], "accepted")
        self.assertEqual(ev["simulated_delta_usd"], -3.0)

    def test_hallucinated_savings_rejected(self):
        ev = validate_plan(USAGE, TOU, self.plan(-20.0))
        self.assertEqual((ev["proposal_status"], ev["rejection_reason"]), ("rejected", "simulation_mismatch"))

    def test_physics_and_confidence(self):
        self.assertEqual(validate_plan(USAGE, TOU, self.plan(-3, kwh=50))["rejection_reason"], "invariant_physics")
        self.assertEqual(validate_plan(USAGE, TOU, self.plan(-3, to=30))["rejection_reason"], "invariant_coverage")
        self.assertEqual(validate_plan(USAGE, TOU, self.plan(-3, conf=0.4))["rejection_reason"], "low_confidence")

    def test_rejection_rate_signal(self):
        evs = [validate_plan(USAGE, TOU, self.plan(p, pid=str(i))) for i, p in enumerate([-3, -3, -20, -3])]
        self.assertEqual(rejection_rate(evs), 0.25)


class LLMTelemetry(unittest.TestCase):
    def test_cost_derived_at_query_time(self):
        span = {"gen_ai.request.model": "model-a", "gen_ai.usage.input_tokens": 2000,
                "gen_ai.usage.output_tokens": 500}
        self.assertAlmostEqual(cost_at_query_time(span), 0.0135)

    def test_harness_repair(self):
        bad = {"calculations": [{"op": "COUNT", "column": "exception.message"}], "breakdowns": ["parent_name"]}
        fixed, changed = repair_query(bad)
        self.assertTrue(changed)
        self.assertEqual(fixed["calculations"], [{"op": "COUNT"}])
        self.assertIn("column", bad["calculations"][0])  # original untouched

    def test_promote_trace_to_eval(self):
        row = promote_to_eval({"trace_id": "t1", "input": "slowest endpoint?", "output": "/a",
                               "user_feedback": "thumbs_down"}, ideal_output="/checkout")
        self.assertEqual(row["expected"], "/checkout")
        self.assertEqual(row["source_trace_id"], "t1")


if __name__ == "__main__":
    unittest.main()
