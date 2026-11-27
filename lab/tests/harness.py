"""Runs the lab without Docker.

  services (real OpenTelemetry SDK) --OTLP/HTTP--> a small OTLP receiver in this process
      --> rows in an embedded ClickHouse engine (chdb), in the Collector exporter's schema

It stands in for the Collector in two places, and says so: it hashes user.email the way
the attributes processor does, and it applies the same tail-sampling policy (errors, slow,
10% of the rest) to fill otel_traces_sampled. Everything else is the real thing: the SDK,
the wire protocol, the SQL engine and the lab queries.

  pip install -r ../app/requirements.txt chdb
"""
import gzip
import hashlib
import os
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(LAB, "loadgen"))
KIND = {0: "Unspecified", 1: "Internal", 2: "Server", 3: "Client", 4: "Producer", 5: "Consumer"}
STATUS = {0: "Unset", 1: "Ok", 2: "Error"}


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def anyvalue(v) -> str:
    which = v.WhichOneof("value")
    if which == "bool_value":
        return "true" if v.bool_value else "false"
    return "" if which is None else str(getattr(v, which))


def attrs(kvs) -> dict:
    return {kv.key: anyvalue(kv.value) for kv in kvs}


def ts(nanos: int) -> str:
    return datetime.fromtimestamp(nanos // 10**9, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + f".{nanos % 10**9:09d}"


class Capture:
    """A minimal OTLP/HTTP receiver: /v1/traces and /v1/metrics, protobuf bodies."""

    def __init__(self):
        self.spans, self.metric_names, self.lock = [], set(), threading.Lock()
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                if self.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                if self.path == "/v1/traces":
                    outer.add_traces(body)
                elif self.path == "/v1/metrics":
                    outer.add_metrics(body)
                self.send_response(200)
                self.send_header("Content-Type", "application/x-protobuf")
                self.end_headers()

            def log_message(self, *a):
                pass

        self.port = free_port()
        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def add_traces(self, body: bytes):
        req = ExportTraceServiceRequest.FromString(body)
        rows = []
        for rs in req.resource_spans:
            res = attrs(rs.resource.attributes)
            for ss in rs.scope_spans:
                for s in ss.spans:
                    rows.append({
                        "Timestamp": ts(s.start_time_unix_nano), "TraceId": s.trace_id.hex(), "SpanId": s.span_id.hex(),
                        "ParentSpanId": s.parent_span_id.hex(), "TraceState": s.trace_state, "SpanName": s.name,
                        "SpanKind": KIND[s.kind], "ServiceName": res.get("service.name", ""), "ResourceAttributes": res,
                        "ScopeName": ss.scope.name, "ScopeVersion": ss.scope.version, "SpanAttributes": attrs(s.attributes),
                        "Duration": s.end_time_unix_nano - s.start_time_unix_nano, "StatusCode": STATUS[s.status.code],
                        "StatusMessage": s.status.message,
                        "Events.Timestamp": [ts(e.time_unix_nano) for e in s.events], "Events.Name": [e.name for e in s.events],
                        "Events.Attributes": [attrs(e.attributes) for e in s.events],
                        "Links.TraceId": [l.trace_id.hex() for l in s.links], "Links.SpanId": [l.span_id.hex() for l in s.links],
                        "Links.TraceState": [l.trace_state for l in s.links], "Links.Attributes": [attrs(l.attributes) for l in s.links]})
        with self.lock:
            self.spans += rows

    def add_metrics(self, body: bytes):
        req = ExportMetricsServiceRequest.FromString(body)
        with self.lock:
            for rm in req.resource_metrics:
                for sm in rm.scope_metrics:
                    for m in sm.metrics:
                        self.metric_names.add(m.name)

    def wait_quiet(self, settle: float = 1.5, timeout: float = 30) -> int:
        """Wait until no new spans arrive for `settle` seconds (the SDK exports in batches)."""
        last, since, end = -1, time.monotonic(), time.monotonic() + timeout
        while time.monotonic() < end:
            n = len(self.spans)
            if n != last:
                last, since = n, time.monotonic()
            elif time.monotonic() - since >= settle:
                break
            time.sleep(0.2)
        return len(self.spans)


class Shop:
    """The three services as local processes, exporting to `otlp_endpoint`."""

    def __init__(self, otlp_endpoint: str):
        self.ports = {name: free_port() for name in ("storefront", "cart", "payments")}
        self.procs = []
        for name, port in self.ports.items():
            env = dict(os.environ, SERVICE=name, PORT=str(port), BUILD_ID="2026.11.2",
                       CART_URL=f"http://127.0.0.1:{self.ports['cart']}", PAYMENTS_URL=f"http://127.0.0.1:{self.ports['payments']}",
                       OTEL_EXPORTER_OTLP_ENDPOINT=otlp_endpoint, OTEL_SEMCONV_STABILITY_OPT_IN="http",
                       OTEL_BSP_SCHEDULE_DELAY="300", METRIC_INTERVAL_MS="1000")
            self.procs.append(subprocess.Popen([sys.executable, "shop.py"], cwd=os.path.join(LAB, "app"), env=env,
                                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        for name, port in self.ports.items():
            self._wait(f"http://127.0.0.1:{port}/healthz")
        self.url = f"http://127.0.0.1:{self.ports['storefront']}"

    @staticmethod
    def _wait(url, timeout=20):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                if requests.get(url, timeout=1).ok:
                    return
            except requests.RequestException:
                time.sleep(0.2)
        raise RuntimeError(f"service did not start: {url}")

    def fault(self, on: bool):
        requests.post(f"http://127.0.0.1:{self.ports['payments']}/admin/fault", json={"on": on}, timeout=5).raise_for_status()

    def stop(self):
        for p in self.procs:
            p.terminate()
        for p in self.procs:
            p.wait(timeout=10)


# ------------------------------------------------- the two things the Collector would do
def scrub(rows: list[dict]) -> list[dict]:
    """Stand-in for the Collector's attributes processor: `{key: user.email, action: hash}`."""
    for r in rows:
        email = r["SpanAttributes"].get("user.email")
        if email:
            r["SpanAttributes"]["user.email"] = hashlib.sha256(email.encode()).hexdigest()
    return rows


def tail_sample(rows: list[dict], slow_ms: int = 500, keep_percent: int = 10) -> list[dict]:
    """Stand-in for the tail_sampling processor: keep traces with an error, slow traces, and N% of the rest."""
    by_trace = {}
    for r in rows:
        by_trace.setdefault(r["TraceId"], []).append(r)
    kept = []
    for tid, spans in by_trace.items():
        error = any(s["StatusCode"] == "Error" for s in spans)
        slow = max(s["Duration"] for s in spans) > slow_ms * 1e6
        if error or slow or int(tid[-8:], 16) % 100 < keep_percent:
            kept += spans
    return kept


# ----------------------------------------------------------------- embedded ClickHouse
class Warehouse:
    def __init__(self):
        from chdb import session
        self.s = session.Session()
        for stmt in statements(read("clickhouse", "schema.sql")):
            self.s.query(stmt)

    def insert(self, table: str, rows: list[dict]):
        import json
        for i in range(0, len(rows), 2000):
            data = "\n".join(json.dumps(r) for r in rows[i:i + 2000])
            self.s.query(f"INSERT INTO otel.{table} FORMAT JSONEachRow {data}")

    def query(self, sql: str, fmt: str = "JSON"):
        import json
        out = self.s.query(sql, fmt)
        return json.loads(out.bytes())["data"] if fmt == "JSON" else out.bytes().decode()

    def run_file(self, name: str, fmt: str = "JSON") -> list:
        return [self.query(q, fmt) for q in statements(read("clickhouse", "queries", name))]


def read(*parts: str) -> str:
    with open(os.path.join(LAB, *parts)) as f:
        return f.read()


def statements(sql: str) -> list[str]:
    lines = [ln for ln in sql.splitlines() if not ln.strip().startswith("--")]
    return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


def run_scenario(baseline: int = 250, faulty: int = 350, seed: int = 7):
    """Healthy traffic, then the fault. Returns (capture, warehouse, stats)."""
    import loadgen
    cap = Capture()
    shop = Shop(f"http://127.0.0.1:{cap.port}")
    try:
        stats = {"baseline": loadgen.run(shop.url, count=baseline, seed=seed)}
        shop.fault(True)
        stats["fault"] = loadgen.run(shop.url, count=faulty, seed=seed + 1)
        time.sleep(1.5)                 # one more metric export interval
        cap.wait_quiet()
    finally:
        shop.stop()
    wh = Warehouse()
    rows = scrub(cap.spans)
    wh.insert("otel_traces", rows)
    wh.insert("otel_traces_sampled", tail_sample(rows))
    return cap, wh, stats


if __name__ == "__main__":
    cap, wh, stats = run_scenario()
    print(f"load: {stats}   spans captured: {len(cap.spans)}   metrics: {sorted(cap.metric_names)}\n")
    for f in sorted(os.listdir(os.path.join(LAB, "clickhouse", "queries"))):
        print(f"=== {f}")
        for q in statements(read("clickhouse", "queries", f)):
            print(wh.query(q, "PrettyCompactNoEscapes"))
