import unittest

from cost_ci import (amdahl_speedup, cost_by, fully_loaded_build_cost, pods_per_node, serverless_request_cost,
                     simulate_ci)


class CostTests(unittest.TestCase):
    def test_bin_packing_book_example(self):
        self.assertEqual(pods_per_node(32, 20), (1, 11.0))  # 11 of 32 cores stranded
        self.assertEqual(pods_per_node(64, 20), (3, 3.0))
        self.assertEqual(pods_per_node(32, 15), (2, 1.0))

    def test_cloud_bill_as_wide_events(self):
        rows = [{"service": "checkout", "usage_type": "NatGateway-Bytes", "team": "pay", "cost_usd": 900},
                {"service": "checkout", "usage_type": "BoxUsage", "team": "pay", "cost_usd": 400},
                {"service": "search", "usage_type": "DataTransfer-Regional", "team": "find", "cost_usd": 1200}]
        self.assertEqual(list(cost_by(rows, "team").items())[0], (("pay",), 1300))
        self.assertEqual(list(cost_by(rows, "usage_type"))[0], ("DataTransfer-Regional",))

    def test_elk_is_not_free(self):
        # book: hardware $80k/month, 3 engineers at $250-300k, recruiting ~$75k each,
        # plus hiring/training time not modelled here -> "over $2M a year"
        low = fully_loaded_build_cost(80_000, 3, 250_000)
        high = fully_loaded_build_cost(80_000, 3, 300_000)
        self.assertGreater(low["first_year"], 1_850_000)
        c = high
        self.assertGreater(c["first_year"], 2_000_000)
        self.assertGreater(c["first_year"], 2 * 80_000 * 12)  # vs ~$960k vendor quote

    def test_serverless_cost(self):
        self.assertAlmostEqual(serverless_request_cost(200, 1.0, 0.0000166667), 0.00000333, places=8)


class CITests(unittest.TestCase):
    def test_retries_hide_failures_but_tax_the_tail(self):
        no_retry = simulate_ci(5000, 10, 0.05, retries=0)
        retry = simulate_ci(5000, 10, 0.05, retries=2)
        self.assertGreater(no_retry["failure_rate"], 0.04)
        self.assertLess(retry["failure_rate"], 0.001)
        self.assertLess(abs(retry["p50"] - no_retry["p50"]), 0.5)  # median barely moves
        self.assertGreater(retry["p99"], 1.8 * no_retry["p99"])  # tail ~doubles

    def test_amdahl(self):
        self.assertLess(amdahl_speedup(0.8, 1000), 5.0)  # 20% serial caps speedup at 5x
        self.assertAlmostEqual(amdahl_speedup(0.5, 2), 4 / 3)


if __name__ == "__main__":
    unittest.main()
