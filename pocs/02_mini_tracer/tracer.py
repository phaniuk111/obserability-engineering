"""POC 2: a tracer from scratch (book ch5 "fancy logs + passing IDs around", ch7).

- Spans are structured events with trace_id, span_id, parent_id, start, duration.
- Intraprocess propagation with contextvars (Python's AsyncLocalStorage/thread-local).
- Interprocess propagation with the W3C `traceparent` header.
- Span links for producer/consumer (Kafka-style) hops.
- Rebuild the tree (DAG) and compute the critical path of a trace (ch18, ch22).
"""
from __future__ import annotations

import contextvars
import os
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

_current: contextvars.ContextVar["Span | None"] = contextvars.ContextVar("current_span", default=None)
TRACEPARENT_RE = re.compile(r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")


def _hex(nbytes: int) -> str:
    return os.urandom(nbytes).hex()


@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_id: str | None
    service: str
    start: float
    duration_ms: float | None = None
    attributes: dict = field(default_factory=dict)
    links: list = field(default_factory=list)  # [{"trace_id":..,"span_id":..}]
    kind: str = "internal"
    sampled: bool = True

    def set(self, **kv):
        self.attributes.update(kv)
        return self

    def to_event(self) -> dict:
        ev = {"name": self.name, "trace.trace_id": self.trace_id, "trace.span_id": self.span_id,
              "trace.parent_id": self.parent_id, "service.name": self.service, "ts": self.start,
              "duration_ms": self.duration_ms, "span.kind": self.kind, **self.attributes}
        if self.links:
            ev["links"] = self.links
        return ev


class Tracer:
    def __init__(self, service: str, exporter: list):
        self.service = service
        self.exporter = exporter

    @contextmanager
    def span(self, name: str, parent: "SpanContext | None" = None, kind: str = "internal",
             links: list | None = None, clock=time.perf_counter, **attrs):
        cur = _current.get()
        if parent is not None:
            trace_id, parent_id, sampled = parent.trace_id, parent.span_id, parent.sampled
        elif cur is not None:
            trace_id, parent_id, sampled = cur.trace_id, cur.span_id, cur.sampled
        else:
            trace_id, parent_id, sampled = _hex(16), None, True
        sp = Span(name, trace_id, _hex(8), parent_id, self.service, clock(), kind=kind,
                  attributes=dict(attrs), links=list(links or []), sampled=sampled)
        token = _current.set(sp)
        try:
            yield sp
        except Exception as exc:  # record and re-raise
            sp.set(error=True, **{"exception.type": type(exc).__name__, "exception.message": str(exc)})
            raise
        finally:
            sp.duration_ms = round((clock() - sp.start) * 1000, 3)
            _current.reset(token)
            if sp.sampled:
                self.exporter.append(sp.to_event())


@dataclass(frozen=True)
class SpanContext:
    trace_id: str
    span_id: str
    sampled: bool = True


def current_context() -> SpanContext | None:
    sp = _current.get()
    return SpanContext(sp.trace_id, sp.span_id, sp.sampled) if sp else None


def inject(headers: dict) -> dict:
    """Write W3C traceparent: version-traceid-parentid-flags."""
    ctx = current_context()
    if ctx:
        headers["traceparent"] = f"00-{ctx.trace_id}-{ctx.span_id}-{'01' if ctx.sampled else '00'}"
    return headers


def extract(headers: dict) -> SpanContext | None:
    m = TRACEPARENT_RE.match(headers.get("traceparent", ""))
    if not m or m.group(1) == "0" * 32 or m.group(2) == "0" * 16:
        return None
    return SpanContext(m.group(1), m.group(2), m.group(3) == "01")


# ----------------------------------------------------------- read-time views
def build_tree(spans: list[dict], trace_id: str) -> dict:
    """SELECT * WHERE trace_id = X, then assemble the DAG from parent ids."""
    mine = [s for s in spans if s["trace.trace_id"] == trace_id]
    by_id = {s["trace.span_id"]: {**s, "children": []} for s in mine}
    roots = []
    for s in by_id.values():
        parent = by_id.get(s["trace.parent_id"])
        (parent["children"] if parent else roots).append(s)
    if len(roots) != 1:
        raise ValueError(f"expected one root, got {len(roots)}")
    return roots[0]


def waterfall(node: dict, depth: int = 0, t0: float | None = None) -> list[str]:
    t0 = node["ts"] if t0 is None else t0
    line = f"{'  ' * depth}{node['name']:<24} +{(node['ts'] - t0) * 1000:7.1f}ms {node['duration_ms']:7.1f}ms"
    out = [line]
    for c in sorted(node["children"], key=lambda c: c["ts"]):
        out += waterfall(c, depth + 1, t0)
    return out


def critical_path(node: dict) -> list[str]:
    """Walk back from the end: at each level follow the child that finishes last
    (the one actually blocking the parent). Optimising anything else won't
    shorten the trace (ch18 Rust-vs-Go build example, ch22 Fin)."""
    path = [node["name"]]
    if not node["children"]:
        return path
    last = max(node["children"], key=lambda c: c["ts"] + c["duration_ms"] / 1000)
    return path + critical_path(last)
