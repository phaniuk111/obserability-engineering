import unittest

from slo import (BurnAlertConfig, SLOConfig, SECONDS_PER_YEAR, budget_minutes, budget_remaining,
                 checkout_sli, evaluate, event_based_bad_fraction, fmt_duration, is_burn_violation,
                 project_linear, project_proportional, relative_burn_threshold, time_based_bad_minutes)


class BudgetMaths(unittest.TestCase):
    def test_three_nines_per_year_and_month(self):
        self.assertEqual(fmt_duration((1 - 0.999) * SECONDS_PER_YEAR), "8h 45m 36s")
        # the book quotes 8h45m57s using a 365.25-day year; same order, check both
        self.assertEqual(fmt_duration((1 - 0.999) * 365.25 * 86400), "8h 45m 58s")
        self.assertAlmostEqual(budget_minutes(0.999, 43830), 43.83, places=2)  # 43m50s, avg month

    def test_four_nines_month(self):
        self.assertAlmostEqual(budget_minutes(0.9999, 43800), 4.38, places=2)

    def test_brownout_equivalence(self):
        # 1% brownout of 99.99% ~ full outage of 99%: both leave >7 hours per 30 days
        self.assertAlmostEqual(budget_minutes(0.99) / 60, 7.2)
        self.assertAlmostEqual(budget_minutes(0.9999) / 0.01 / 60, 7.2)


class SLITests(unittest.TestCase):
    def test_eligibility_and_success(self):
        ok = {"http.request.method": "POST", "http.route": "/checkout", "http.response.status_code": 200,
              "duration_ms": 900}
        slow = dict(ok, duration_ms=5000)
        probe = dict(ok, **{"user_agent.original": "kube-probe/1.29"})
        child = dict(ok, **{"trace.parent_id": "abc"})
        get = dict(ok, **{"http.request.method": "GET"})
        self.assertEqual([checkout_sli(e) for e in (ok, slow, probe, child, get)], [True, False, None, None, None])
        self.assertEqual(evaluate([ok, slow, probe], checkout_sli), (1, 1))


class BurnAlerts(unittest.TestCase):
    def test_relative_burn_book_example(self):
        # 10M req/month, 99.9%, 15-min windows: ~3.47 allowed; 4x ~13.9, 20x ~69.4
        self.assertAlmostEqual(relative_burn_threshold(10_000_000, 0.999, 15, 1), 3.47, places=2)
        self.assertEqual(int(relative_burn_threshold(10_000_000, 0.999, 15, 4)), 13)
        self.assertEqual(int(relative_burn_threshold(10_000_000, 0.999, 15, 20)), 69)

    def test_short_term_linear_vs_proportional(self):
        budget = 438  # 1% of 43,800 units/month
        self.assertEqual(project_linear(5, 6, 24) + 5, 25)  # 25 < 438, fine
        self.assertEqual(project_linear(50, 24, 192) + 50, 450)  # exhaust in ~8 days
        linear = project_linear(25, 6, 24) + 5 * 0  # 100 more
        proportional = project_proportional(25, 50, 1440)  # 50% of a normal day
        self.assertLess(linear, budget)
        self.assertEqual(proportional, 720)
        self.assertGreater(proportional, budget)

    def test_context_aware_port(self):
        slo = SLOConfig(time_period_days=30, budget_ppm=10_000)  # 99%
        now = 30 * 1440
        # 29 healthy days at 1 fail / 300 units, then one bad day: 130 fails of 1460
        ts, tot, fl = [], {}, {}
        for d in range(29):
            t = d * 1440
            ts.append(t); tot[t] = 1310; fl[t] = 10
        t = 29 * 1440 + 60
        ts.append(t); tot[t] = 1460; fl[t] = 130
        four_days = BurnAlertConfig(exhaustion_minutes=4 * 1440)
        self.assertTrue(is_burn_violation(now, four_days, slo, ts, tot, fl))
        fl[t] = 10
        self.assertFalse(is_burn_violation(now, four_days, slo, ts, tot, fl))

    def test_budget_remaining(self):
        self.assertAlmostEqual(budget_remaining(43_800, 285, 0.99), 1 - 285 / 438)


class TimeVsEventSLI(unittest.TestCase):
    def test_one_minute_at_94_percent_good(self):
        minute = [100.0] * 94 + [400.0] * 6  # 94% under 300 ms
        self.assertEqual(time_based_bad_minutes([minute], 300), 1)  # whole minute burned
        self.assertAlmostEqual(event_based_bad_fraction([minute], 300), 0.06)  # only 6% burned
        # one bad minute = ~23% of a 4.38-minute 99.99% budget (book rounds to 25%)
        self.assertAlmostEqual(1 / 4.38, 0.228, places=3)


if __name__ == "__main__":
    unittest.main()
