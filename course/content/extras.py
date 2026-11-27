"""Second-pass additions: hands-on lab per chapter, official documentation, and what has
changed since the book was written. Every URL here was opened or returned by a search
during the review on 2026-11-27; nothing is linked from memory."""

REPO = "https://github.com/phaniuk111/obserability-engineering/blob/main/"

LAB_TITLES = {1: ("Follow one request", "lab/labs/01-traces.md"), 2: ("Wide events and high cardinality", "lab/labs/02-wide-events.md"),
              3: ("Find the culprit without a hypothesis", "lab/labs/03-core-analysis-loop.md"), 4: ("SLOs and burn alerts", "lab/labs/04-slo.md"),
              5: ("Sampling", "lab/labs/05-sampling.md"), 6: ("The pipeline", "lab/labs/06-pipeline.md"),
              7: ("Storage", "lab/labs/07-storage.md"), 8: ("From lab to production", "lab/labs/08-production.md")}
LABS = {"ch01": 2, "ch05": 2, "ch06": 1, "ch07": 1, "ch08": 3, "ch11": 4, "ch12": 4, "ch13": 7, "ch14": 7,
        "ch15": 5, "ch16": 6, "ch29": 8, "ch30": 8, "ch31": 6}
# Knowledge-map / requirements "POC" column: old POC number -> lab number (None = no lab).
POC_TO_LAB = {"01": 2, "02": 1, "03": 3, "04": 4, "05": 5, "06": 7, "07": 6, "08": None, "09": None, "10": None}

EXERCISES = {
 "ch01": "Lab 2: run `make q F=02_wide_events`. Pick one result from 2b or 2c that your current metrics could not produce, and say why.",
 "ch05": "Labs 1 and 2: open a checkout trace in Jaeger, then run query 2d and explain why the average of averages differs from the true average.",
 "ch07": "Lab 1: read `lab/app/shop.py`, add one attribute and one custom span of your own, rebuild, and find them in ClickHouse. Explain why `send_receipt` uses a link, not a parent.",
 "ch08": "Lab 3: switch the fault on and run the BubbleUp query. Then change the fault so it needs two attributes at once and see whether the query still surfaces it.",
 "ch11": "Lab 4: rewrite the SLI in `lab/clickhouse/queries/04_slo.sql` for another endpoint, with an explicit eligibility clause.",
 "ch12": "Lab 4: with the fault on, watch the burn alert go from pending to firing in Prometheus. Change the target to 99.9% in query 4a and explain the new burn rate.",
 "ch13": "Lab 7: run `make q F=07_storage`, add a bloom-filter skip index on the attribute values, and compare the plan for query 7d.",
 "ch15": "Lab 5: run `make q F=05_sampling`. Change the baseline policy to 1% in the Collector and correct the weight in query 5b.",
 "ch16": "Lab 6: stop ClickHouse for 30 seconds and read the Collector's retry logs. Then add a processor action that deletes `client.address`.",
 "ch17": "Write three invariants for an AI-proposed change in a system you know (a hard limit, a rollback condition, a required approval) and say where each is enforced.",
 "ch18": "Export the step timings of one CI run, draw the dependency graph and mark the critical path. Which step would you speed up first, and why not the slowest one?",
 "ch19": "List three user intentions in your mobile app (for example, start checkout) and the outcome event that completes each. Each pair is an SLI.",
 "ch20": "For one cluster, compare requested and used CPU per node and estimate the waste. Then name one telemetry stream you could sample or route to cheaper storage.",
 "ch21": "Add `gen_ai.request.model` and the token-count attributes to one LLM call you own, then compute cost per request from the spans.",
 "ch29": "Place five components of your stack on the 2×2. Price one 'free' open-source option in full: hardware, three engineers, on-call, upgrades.",
}

OTEL = "opentelemetry.io"
DOCS = {
 "ch06": [["W3C Trace Context", "https://www.w3.org/TR/trace-context/", "The traceparent and tracestate headers, field by field"]],
 "ch07": [["OpenTelemetry semantic conventions: HTTP spans", "https://opentelemetry.io/docs/specs/semconv/http/http-spans", "Stable attribute names such as http.request.method"],
          ["HTTP conventions migration guide", "https://opentelemetry.io/docs/specs/semconv/http/migration-guide/", "Old name → new name table"],
          ["OpenTelemetry eBPF Instrumentation (OBI)", "https://opentelemetry.io/docs/zero-code/obi/", "Zero-code instrumentation from the kernel"],
          ["Weaver", "https://github.com/open-telemetry/weaver", "Define, lint and live-check telemetry schemas"],
          ["AWS: migrating from X-Ray SDKs to OpenTelemetry", "https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-migration.html", "Concept mapping and timeline"]],
 "ch10": [["Amazon CloudWatch investigations (GA announcement)", "https://aws.amazon.com/about-aws/whats-new/2025/06/ga-accelerate-troubleshooting-amazon-cloudwatch-investigations", "AWS's AI-assisted investigation feature"]],
 "ch12": [["Google SRE Workbook: Alerting on SLOs", "https://sre.google/workbook/alerting-on-slos/", "Multi-window, multi-burn-rate alerts"]],
 "ch14": [["ClickHouse MergeTree engine", "https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree", "Parts, granules, sparse primary index"],
          ["MergeTree settings: max_bytes_*", "https://clickhouse.com/docs/reference/settings/merge-tree-settings/max-bytes", "Where the 150 GB merged-part default comes from"],
          ["Collector ClickHouse exporter", "https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/clickhouseexporter", "The otel_traces schema used in the lab"]],
 "ch15": [["OpenTelemetry: Sampling", "https://opentelemetry.io/docs/concepts/sampling/", "Head vs tail, when to sample at all"],
          ["Tail sampling processor", "https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/processor/tailsamplingprocessor", "Policies, decision_wait, scaling"],
          ["Load balancing exporter", "https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/loadbalancingexporter", "Routing by trace id in front of tail sampling"]],
 "ch16": [["Collector resiliency", "https://opentelemetry.io/docs/collector/resiliency/", "Sending queue, retries, persistent storage"],
          ["Deprecating the Collector batch processor", "https://opentelemetry.io/blog/2026/collector-batching-migration/", "Exporter-level batching"],
          ["Span metrics connector", "https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/connector/spanmetricsconnector", "RED metrics from spans"],
          ["OpAMP specification", "https://opentelemetry.io/docs/specs/opamp", "Remote management of agent fleets"],
          ["CloudWatch OTLP endpoints", "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLPEndpoint.html", "Sending OTLP straight to AWS, SigV4-signed"]],
 "ch18": [["OpenTelemetry semantic conventions: CI/CD", "https://opentelemetry.io/docs/specs/semconv/cicd/", "Pipeline run and task spans"]],
 "ch21": [["GenAI semantic conventions: spans", "https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/", "gen_ai.* attributes for model calls"],
          ["GenAI conventions repository", "https://github.com/open-telemetry/semantic-conventions-genai", "Where the gen_ai.* definitions now live"]],
 "ch29": [["AWS services in maintenance", "https://docs.aws.amazon.com/general/latest/gr/maintenance_services.html", "Check before you depend on a managed service"]],
 "ch31": [["Build a custom Collector (OCB)", "https://opentelemetry.io/docs/collector/extend/ocb/", "Your own distribution from a manifest"],
          ["Observability by design with Weaver", "https://opentelemetry.io/blog/2025/otel-weaver/", "Registry check, code generation, live check"],
          ["Collector management with OpAMP", "https://opentelemetry.io/docs/collector/management/", "Central control of Collector config"]],
}

# What changed after the book's examples were written. Short, dated, each with its source in DOCS or below.
FRESH = {
 "ch06": ["Trace flags are a bit field: only the lowest bit means 'sampled', and version `ff` is invalid. Trace Context Level 2 adds a 'random trace id' flag, so compare bits, not the string `01`."],
 "ch07": ["AWS put the X-Ray SDKs and daemon into maintenance on 25 Feb 2026, with end of support on 25 Feb 2027, and recommends OpenTelemetry instrumentation instead.",
          "The GenAI (`gen_ai.*`) conventions moved to their own repository in 2026 and are still marked as in development, so expect renames."],
 "ch10": ["The AWS feature previewed as 'Amazon Q Developer operational investigations' became generally available in June 2025 under the name CloudWatch investigations."],
 "ch11": ["Check the arithmetic in the chapter's LLM transcript: 99.95% availability allows about 4.4 hours of downtime a year (about 22 minutes a month), not the '~42 minutes' the model says. It makes the chapter's own point: treat the model as a draft generator and verify."],
 "ch15": ["Tail sampling only works if every span of a trace reaches the same Collector instance; with more than one, put a load-balancing tier that routes by trace id in front."],
 "ch16": ["The Collector's `batch` processor is deprecated in favour of batching inside each exporter's `sending_queue`; the project's timeline has it warning from v0.171 (Feb 2027) and removed in v0.177 (May 2027).",
          "The OTLP exporters are now called `otlp_grpc` and `otlp_http`; `otlp` and `otlphttp` remain as deprecated aliases."],
 "ch18": ["OpenTelemetry now has CI/CD semantic conventions (first attributes in v1.27.0), so pipeline traces can use standard names."],
 "ch19": ["CloudWatch Evidently was discontinued in October 2025 (AWS points to AppConfig feature flags) and Amazon Pinpoint support ended on 30 October 2026."],
 "ch23": ["AWS Proton support ended on 7 October 2026; AWS's migration guide points to Backstage-based options such as Harmonix."],
 "ch31": ["The chapter's examples use `db.system`; current convention docs use `db.system.name`. A schema check in CI is what catches this kind of drift."],
}
MORE_SOURCES = [
 ["X-Ray SDK and daemon support timeline", "https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-daemon-timeline.html"],
 ["Support for CloudWatch Evidently ending", "https://aws.amazon.com/blogs/mt/support-for-amazon-cloudwatch-evidently-ending-soon"],
 ["Amazon Pinpoint end of support", "https://docs.aws.amazon.com/pinpoint/latest/userguide/migrate.html"],
 ["AWS Proton deprecation and migration guide", "https://docs.aws.amazon.com/proton/latest/userguide/proton-end-of-support.html"],
 ["OTLP/HTTP exporter (component id note)", "https://pkg.go.dev/go.opentelemetry.io/collector/exporter/otlphttpexporter"],
 ["Trace Context Level 2", "https://www.w3.org/TR/trace-context-2/"],
 ["OpenTelemetry CI/CD observability announcement", "https://opentelemetry.io/blog/2025/otel-cicd-sig/"],
 ["SigV4 authenticator extension", "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/extension/sigv4authextension/README.md"],
 ["AWS S3 exporter", "https://pkg.go.dev/github.com/open-telemetry/opentelemetry-collector-contrib/exporter/awss3exporter"],
 ["CloudWatch and OpenTelemetry", "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OpenTelemetry-Sections.html"],
]
