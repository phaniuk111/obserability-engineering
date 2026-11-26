import unittest

from tracer import SpanContext, Tracer, build_tree, critical_path, extract, inject, waterfall


class FakeClock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t

    def advance(self, ms):
        self.t += ms / 1000


class TracerTests(unittest.TestCase):
    def setUp(self):
        self.out = []
        self.clock = FakeClock()

    def test_parent_child_and_tree(self):
        api = Tracer("checkout-api", self.out)
        with api.span("GET /checkout", clock=self.clock) as root:
            with api.span("auth.verify", clock=self.clock):
                self.clock.advance(12)
            with api.span("db.query_cart", clock=self.clock):
                self.clock.advance(89)
            self.clock.advance(5)
        tree = build_tree(self.out, root.trace_id)
        self.assertEqual(tree["name"], "GET /checkout")
        self.assertEqual([c["name"] for c in tree["children"]], ["auth.verify", "db.query_cart"])
        self.assertIsNone(tree["trace.parent_id"])
        self.assertEqual(len(waterfall(tree)), 3)

    def test_traceparent_round_trip_across_services(self):
        a, b = Tracer("frontend", self.out), Tracer("payments", self.out)
        with a.span("POST /pay") as root:
            headers = inject({})
            self.assertRegex(headers["traceparent"], r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$")
        ctx = extract(headers)
        with b.span("charge", parent=ctx, kind="server") as child:
            pass
        self.assertEqual(child.trace_id, root.trace_id)
        self.assertEqual(child.parent_id, root.span_id)

    def test_invalid_traceparent_rejected(self):
        self.assertIsNone(extract({"traceparent": "00-" + "0" * 32 + "-" + "a" * 16 + "-01"}))
        self.assertIsNone(extract({"traceparent": "garbage"}))

    def test_unsampled_context_is_not_exported(self):
        t = Tracer("svc", self.out)
        with t.span("x", parent=SpanContext("a" * 32, "b" * 16, sampled=False)):
            pass
        self.assertEqual(self.out, [])

    def test_exception_recorded(self):
        t = Tracer("svc", self.out)
        with self.assertRaises(RuntimeError):
            with t.span("boom"):
                raise RuntimeError("nope")
        self.assertTrue(self.out[0]["error"])

    def test_span_links_for_async_consumer(self):
        t = Tracer("orders", self.out)
        with t.span("messaging.publish", kind="producer") as pub:
            pass
        consumer = Tracer("payments", self.out)
        with consumer.span("messaging.process", kind="consumer",
                           links=[{"trace_id": pub.trace_id, "span_id": pub.span_id}]) as proc:
            pass
        self.assertNotEqual(proc.trace_id, pub.trace_id)  # new trace, linked not parented
        self.assertEqual(self.out[-1]["links"][0]["span_id"], pub.span_id)

    def test_critical_path_ignores_parallel_shorter_work(self):
        # React 2 min, Go 4 min (got slower), Rust 9 min run in parallel after prebuild.
        root = {"name": "workflow", "ts": 0, "duration_ms": 660_000, "children": [
            {"name": "prebuild", "ts": 0, "duration_ms": 60_000, "children": []},
            {"name": "react", "ts": 60, "duration_ms": 120_000, "children": []},
            {"name": "go", "ts": 60, "duration_ms": 240_000, "children": []},
            {"name": "rust", "ts": 60, "duration_ms": 540_000, "children": []},
        ]}
        self.assertEqual(critical_path(root), ["workflow", "rust"])


if __name__ == "__main__":
    unittest.main()
