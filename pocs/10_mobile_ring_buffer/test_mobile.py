import random
import unittest

from mobile import Device, RingBuffer, Rule, completion_rate

CHECKOUT_RULE = Rule("checkout_abandon", start="view_checkout", success="checkout_complete",
                     abandon_events=("leave_checkout",), timeout_s=15)


class RingBufferTests(unittest.TestCase):
    def test_bounded(self):
        rb = RingBuffer(3)
        for i in range(10):
            rb.log({"i": i})
        self.assertEqual([e["i"] for e in rb.dump()], [7, 8, 9])


class ControlPlaneTests(unittest.TestCase):
    def test_nothing_uploaded_without_a_matching_rule(self):
        d = Device({"app_version": "3.2.8"})
        for i in range(100):
            d.log("tap", i)
        self.assertEqual(d.uploads, [])

    def test_abandon_dumps_session(self):
        d = Device({"app_version": "3.2.8", "device_model": "pixel-4"})
        d.apply_config([CHECKOUT_RULE])
        d.log("view_cart", 0)
        d.log("view_checkout", 1)
        d.log("tap_submit", 2, enabled=False)
        d.log("leave_checkout", 5)
        self.assertEqual(d.counters["checkout_abandon"], 1)
        up = d.uploads[0]
        self.assertEqual(up["reason"], "abandon:leave_checkout")
        self.assertIn("tap_submit", [e["name"] for e in up["session"]])

    def test_timeout_and_success(self):
        d = Device({})
        d.apply_config([CHECKOUT_RULE])
        d.log("view_checkout", 0)
        d.log("scroll", 20)  # 20 s > 15 s
        self.assertEqual(d.uploads[0]["reason"], "timeout")
        d.log("view_checkout", 30)
        d.log("checkout_complete", 35)
        self.assertEqual(len(d.uploads), 1)

    def test_cohort_targeting(self):
        rule = Rule("old_android", "view_checkout", "checkout_complete", ("leave_checkout",), 15,
                    match={"os": "android-12"})
        a, b = Device({"os": "android-12"}), Device({"os": "ios-18"})
        for d in (a, b):
            d.apply_config([rule])
            d.log("view_checkout", 0)
            d.log("leave_checkout", 1)
        self.assertEqual((len(a.uploads), len(b.uploads)), (1, 0))


class UserFocusedSLITests(unittest.TestCase):
    def test_discount_code_bug_shows_in_completion_rate(self):
        rng = random.Random(4)
        events = []
        for i in range(2000):
            code = rng.choice(["NONE", "NONE", "NEW-FORMAT"])
            events.append({"name": "start_checkout", "checkout_id": i, "discount_code_format": code})
            p = 0.85 if code == "NONE" else 0.40  # new format disables Submit first time
            if rng.random() < p:
                events.append({"name": "end_checkout", "checkout_id": i})
        by = completion_rate(events, by="discount_code_format")
        self.assertGreater(by["NONE"] - by["NEW-FORMAT"], 0.35)
        self.assertLess(completion_rate(events)["all"], 0.75)


if __name__ == "__main__":
    unittest.main()
