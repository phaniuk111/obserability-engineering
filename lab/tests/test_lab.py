"""End-to-end tests for the lab, without Docker.

Real: the OpenTelemetry SDK in three service processes, OTLP/HTTP on the wire, the
ClickHouse SQL engine (chdb) and every query file the labs use.
Stand-ins: the Collector's PII hashing and tail sampling (see harness.py).

  python3 -m unittest -v        (about a minute)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "collector"))
import harness  # noqa: E402


class TestLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cap, cls.wh, cls.stats = harness.run_scenario(baseline=200, faulty=300)
        cls.spans = cls.cap.spans

    # ---------------------------------------------------------------- instrumentation
    def test_three_services_report_and_requests_succeed_before_the_fault(self):
        self.assertEqual({s["ServiceName"] for s in self.spans}, {"storefront", "cart", "payments"})
        self.assertEqual(self.stats["baseline"], {"ok": 200, "error": 0})
        self.assertGreater(self.stats["fault"]["error"], 0)

    def test_one_trace_spans_all_services_with_intact_parent_links(self):
        root = next(s for s in self.spans if s["SpanName"] == "POST /checkout")
        trace = [s for s in self.spans if s["TraceId"] == root["TraceId"]]
        self.assertEqual({s["ServiceName"] for s in trace}, {"storefront", "cart", "payments"})
        ids = {s["SpanId"] for s in trace}
        self.assertEqual([s["SpanName"] for s in trace if s["ParentSpanId"] == ""], ["POST /checkout"])
        self.assertTrue(all(s["ParentSpanId"] in ids for s in trace if s["ParentSpanId"]))
        kinds = {(s["ServiceName"], s["SpanKind"]) for s in trace}
        self.assertLessEqual({("storefront", "Server"), ("storefront", "Client"), ("payments", "Server"), ("cart", "Internal")}, kinds)

    def test_wide_event_and_stable_semantic_conventions(self):
        root = next(s for s in self.spans if s["SpanName"] == "POST /checkout")
        a = root["SpanAttributes"]
        for key in ("app.user.id", "app.user.tier", "app.payment.method", "app.discount.format", "app.build.id",
                    "http.request.method", "http.response.status_code", "http.route", "url.path"):
            self.assertIn(key, a)
        self.assertNotIn("http.method", a)                       # old attribute name, pre-stable
        self.assertEqual(root["ResourceAttributes"]["service.version"], "2026.11.2")

    def test_baggage_reaches_payments(self):
        rows = self.wh.run_file("01_traces.sql")[3]
        self.assertTrue(rows)
        self.assertTrue(all(r["tier_at_storefront"] == r["tier_at_payments"] for r in rows))

    def test_async_job_is_a_new_trace_linked_to_its_cause(self):
        job = next(s for s in self.spans if s["SpanName"] == "send_receipt")
        self.assertEqual(job["ParentSpanId"], "")
        cause = next(s for s in self.spans if s["SpanId"] == job["Links.SpanId"][0])
        self.assertEqual(cause["SpanName"], "POST /checkout")
        self.assertNotEqual(cause["TraceId"], job["TraceId"])
        self.assertEqual(cause["SpanAttributes"]["app.order.id"], job["SpanAttributes"]["app.order.id"])

    def test_failure_is_recorded_as_an_exception_event(self):
        bad = next(s for s in self.spans if s["SpanName"] == "validate_discount" and s["StatusCode"] == "Error")
        self.assertIn("exception", bad["Events.Name"])
        self.assertEqual(bad["Events.Attributes"][0]["exception.type"], "TimeoutError")

    def test_metrics_exported_with_low_cardinality_only(self):
        self.assertIn("shop.checkout.duration", self.cap.metric_names)
        self.assertIn("http.server.request.duration", self.cap.metric_names)

    # --------------------------------------------------------------------- lab queries
    def test_lab1_waterfall_starts_at_the_root(self):
        slowest, waterfall, links, _ = self.wh.run_file("01_traces.sql")
        self.assertEqual(slowest[0]["discount"], "v2")
        self.assertEqual((waterfall[0]["SpanName"], waterfall[0]["start_ms"]), ("POST /checkout", 0))
        self.assertGreaterEqual(len(waterfall), 6)
        self.assertTrue(links and all(r["order_id"] for r in links))

    def test_lab2_high_cardinality_is_queryable(self):
        card, by_dims, users, avg = self.wh.run_file("02_wide_events.sql")
        distinct = {r["attribute"]: int(r["distinct_values"]) for r in card}
        self.assertGreater(distinct["app.user.id"], 400)
        self.assertEqual(distinct["app.user.tier"], 3)
        self.assertTrue(by_dims and users)
        self.assertGreater(avg[0]["avg_of_averages"], avg[0]["true_average"] * 1.5)

    def test_lab3_bubbleup_finds_the_culprit_without_a_hypothesis(self):
        top = self.wh.run_file("03_bubbleup.sql")[0][0]
        self.assertEqual((top["attribute"], top["value"]), ("app.discount.format", "v2"))
        self.assertGreater(top["gap"], 0.8)

    def test_lab4_event_based_slo(self):
        summary, per_minute, compare = self.wh.run_file("04_slo.sql")
        s = summary[0]
        self.assertEqual(int(s["eligible"]), 500)
        self.assertEqual(int(s["good"]) + int(s["bad"]), 500)
        self.assertGreater(s["burn_rate"], 1)                     # burning faster than the budget allows
        self.assertAlmostEqual(s["burn_rate"], (int(s["bad"]) / 500) / 0.01, places=1)
        self.assertTrue(per_minute)
        self.assertGreaterEqual(compare[0]["time_based_bad_percent"], compare[0]["event_based_bad_percent"])

    def test_lab5_sampling_keeps_every_error_and_weights_recover_the_total(self):
        kept, estimate, errors = self.wh.run_file("05_sampling.sql")
        self.assertLess(kept[0]["kept_percent"], 30)
        e = estimate[0]
        true_total = int(e["true_total"])
        self.assertLess(abs(int(e["weighted_estimate"]) - true_total) / true_total, 0.25)
        self.assertLess(int(e["naive_total"]), true_total / 3)
        self.assertGreater(e["naive_error_percent"], e["weighted_error_percent"] * 3)
        self.assertEqual(errors[0]["error_traces"], errors[0]["error_traces_kept"])

    def test_lab6_no_plaintext_email_is_stored(self):
        pii, distinct = self.wh.run_file("06_pipeline.sql")
        self.assertEqual(int(pii[0]["still_plaintext"]), 0)
        self.assertGreater(int(pii[0]["events_with_email"]), 0)
        self.assertEqual(distinct[0]["distinct_users"], distinct[0]["distinct_hashed_emails"])

    def test_lab7_storage_queries_run(self):
        parts, keys = self.wh.run_file("07_storage.sql")[:2]
        self.assertGreater(parts[0]["compression_ratio"], 2)
        self.assertIn("ServiceName", keys[0]["sorting_key"])
        for q in harness.statements(harness.read("clickhouse", "queries", "07_storage.sql"))[2:]:
            self.assertIn("ReadFromMergeTree", self.wh.query(q, "TSV"))


class TestConfigs(unittest.TestCase):
    """Structural checks on the Collector configs (not a substitute for `otelcol validate`)."""

    def setUp(self):
        import check_config
        self.cc = check_config

    def test_all_collector_configs_are_clean(self):
        files = self.cc.all_configs()
        self.assertEqual(len(files), 3)
        for f in files:
            self.assertEqual(self.cc.lint(self.cc.load(f)), [], f)

    def test_metrics_are_taken_before_sampling_everywhere(self):
        for name in ("local.yaml", os.path.join("production", "gateway-collector.yaml")):
            p = self.cc.load(os.path.join(self.cc.HERE, name))["service"]["pipelines"]
            self.assertIn("spanmetrics", p["traces/in"]["exporters"], name)
            self.assertNotIn("tail_sampling", p["traces/in"]["processors"], name)
            self.assertEqual(p["traces/sampled"]["processors"][0], "tail_sampling", name)

    def test_lint_catches_orphans_and_bad_order(self):
        import copy
        good = self.cc.load(os.path.join(self.cc.HERE, "production", "gateway-collector.yaml"))
        bad = copy.deepcopy(good)
        bad["service"]["pipelines"]["traces/sampled"]["processors"] = []
        del bad["exporters"]["otlp_http/observability_vendor"]["sending_queue"]
        problems = "\n".join(self.cc.lint(bad))
        self.assertIn("processor tail_sampling is defined but never used", problems)
        self.assertIn("extension file_storage/queue is enabled but no exporter references it", problems)
        bad = copy.deepcopy(good)
        bad["processors"]["k8sattributes"] = {}
        bad["service"]["pipelines"]["traces/sampled"]["processors"] = ["tail_sampling", "k8sattributes"]
        bad["service"]["pipelines"]["traces/in"]["exporters"].remove("forward/to_sampling")
        problems = "\n".join(self.cc.lint(bad))
        self.assertIn("must run before tail_sampling", problems)
        self.assertIn("connector forward/to_sampling must be an exporter in one pipeline and a receiver in another", problems)

    def test_production_gateway_is_durable_signed_and_routed(self):
        gw = self.cc.load(os.path.join(self.cc.HERE, "production", "gateway-collector.yaml"))
        self.assertEqual(gw["exporters"]["otlp_http/observability_vendor"]["sending_queue"]["storage"], "file_storage/queue")
        self.assertEqual(gw["exporters"]["prometheusremotewrite/amp"]["auth"]["authenticator"], "sigv4auth")
        agent = self.cc.load(os.path.join(self.cc.HERE, "production", "agent-collector.yaml"))
        self.assertEqual(agent["exporters"]["load_balancing/gateway"]["routing_key"], "traceID")

    def test_compose_and_prometheus_files_are_consistent(self):
        import yaml
        compose = yaml.safe_load(harness.read("docker-compose.yaml"))
        services = compose["services"]
        for name in ("storefront", "cart", "payments", "loadgen", "otel-collector", "clickhouse", "prometheus", "jaeger", "grafana"):
            self.assertIn(name, services)
        for name in ("storefront", "cart", "payments"):
            env = services[name]["environment"]
            self.assertEqual(env["OTEL_EXPORTER_OTLP_ENDPOINT"], "http://otel-collector:4318")
            self.assertEqual(env["SERVICE"], name)
        local = self.cc.load(os.path.join(self.cc.HERE, "local.yaml"))
        ns = local["connectors"]["spanmetrics"]["namespace"]
        rules = harness.read("prometheus", "rules.yml")
        yaml.safe_load(rules)
        self.assertIn(f"{ns}_calls_total", rules)
        scrape = yaml.safe_load(harness.read("prometheus", "prometheus.yml"))["scrape_configs"][0]
        port = local["exporters"]["prometheus"]["endpoint"].split(":")[-1]
        self.assertEqual(scrape["static_configs"][0]["targets"], [f"otel-collector:{port}"])


if __name__ == "__main__":
    unittest.main()
