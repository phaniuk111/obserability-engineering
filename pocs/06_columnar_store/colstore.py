"""POC 6: a tiny Retriever-style columnar store (book ch13, ch14).

- Append-only segments per tenant; finalise on age / row count / size.
- Segment metadata keeps min/max timestamp -> prune segments by time range.
- Inside a segment, one column per field (+ timestamp index); dictionary
  encoding for repetitive strings; only referenced columns are read
  (ClickHouse calls this lazy materialisation).
- Query: filter -> group -> aggregate per segment -> merge -> top K.
- Calculated fields at read time (COALESCE for a field rename).
- Parallel segment scan with "RPC impatience": re-issue the slowest ~10%.
- TSDB cardinality explosion: series count when a tag is added.
"""
from __future__ import annotations

import concurrent.futures as cf
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable


class Column:
    """Dictionary-encoded column: values stored as small ints + a dictionary."""

    def __init__(self):
        self.dict: dict = {}
        self.rev: list = []
        self.codes: list[int] = []  # -1 = null (sparse)

    def append(self, v):
        if v is None:
            self.codes.append(-1)
            return
        code = self.dict.get(v)
        if code is None:
            code = self.dict[v] = len(self.rev)
            self.rev.append(v)
        self.codes.append(code)

    def get(self, i):
        c = self.codes[i]
        return None if c < 0 else self.rev[c]

    def pad(self, n):
        while len(self.codes) < n:
            self.codes.append(-1)


@dataclass
class Segment:
    min_ts: float = math.inf
    max_ts: float = -math.inf
    rows: int = 0
    bytes: int = 0
    created: float = field(default_factory=time.time)
    finalized: bool = False
    columns: dict = field(default_factory=lambda: defaultdict(Column))
    reads: int = 0  # how many column reads were performed (to prove pruning)

    def append(self, event: dict):
        ts = event["ts"]
        self.min_ts, self.max_ts = min(self.min_ts, ts), max(self.max_ts, ts)
        for k, v in event.items():
            col = self.columns[k]
            col.pad(self.rows)
            col.append(v)
        self.rows += 1
        self.bytes += len(repr(event))

    def column(self, name: str):
        self.reads += 1
        col = self.columns.get(name)
        if col is None:
            return [None] * self.rows
        col.pad(self.rows)
        return [col.get(i) for i in range(self.rows)]


class Store:
    def __init__(self, max_rows=250_000, max_bytes=1_000_000_000, max_age_s=3600):
        self.segments: list[Segment] = []
        self.active: Segment | None = None
        self.limits = (max_rows, max_bytes, max_age_s)

    def ingest(self, event: dict):
        if self.active is None:
            self.active = Segment()
            self.segments.append(self.active)
        self.active.append(event)
        rows, size, age = self.limits
        if (self.active.rows >= rows or self.active.bytes >= size
                or time.time() - self.active.created >= age):
            self.active.finalized = True
            self.active = None

    # ----------------------------------------------------------- query
    def query(self, t0: float, t1: float, *, where: Callable[[dict], bool] = lambda r: True,
              columns: tuple[str, ...], group_by: tuple[str, ...] = (), agg: str = "count",
              field_: str | None = None, top_k: int = 20, calculated: dict | None = None,
              parallel: bool = False, slow_segment: Callable[[Segment], float] | None = None):
        calculated = calculated or {}
        overlapping = [s for s in self.segments if s.max_ts >= t0 and s.min_ts <= t1]

        def scan(seg: Segment):
            if slow_segment:
                time.sleep(slow_segment(seg))
            needed = set(columns) | set(group_by) | ({field_} if field_ else set()) | {"ts"}
            needed -= set(calculated)
            for c in calculated.values():
                needed |= set(c[0])
            cols = {c: seg.column(c) for c in sorted(needed)}
            partial = defaultdict(lambda: [0, 0.0, -math.inf])  # count, sum, max
            for i in range(seg.rows):
                row = {c: v[i] for c, v in cols.items()}
                if not (t0 <= row["ts"] <= t1):
                    continue
                for name, (inputs, fn) in calculated.items():
                    row[name] = fn(*[row[x] for x in inputs])
                if not where(row):
                    continue
                key = tuple(row.get(g) for g in group_by)
                a = partial[key]
                a[0] += 1
                if field_ and row.get(field_) is not None:
                    a[1] += row[field_]
                    a[2] = max(a[2], row[field_])
            return dict(partial)

        partials = hedged_map(scan, overlapping) if parallel else [scan(s) for s in overlapping]
        merged = defaultdict(lambda: [0, 0.0, -math.inf])
        for p in partials:
            for k, (c, s, m) in p.items():
                a = merged[k]
                a[0] += c; a[1] += s; a[2] = max(a[2], m)
        out = {}
        for k, (c, s, m) in merged.items():
            out[k] = {"count": c, "sum": s, "avg": s / c if c else None, "max": m}[agg]
        ranked = sorted(out.items(), key=lambda kv: -(kv[1] or 0))
        return ranked[:top_k], len(overlapping)


def hedged_map(fn, items, hedge_after=0.9, workers=16):
    """Run fn over items in parallel; once `hedge_after` of them are done,
    re-issue the stragglers and take whichever copy finishes first."""
    results: dict[int, object] = {}
    pool = cf.ThreadPoolExecutor(max_workers=workers)
    try:
        futs = {pool.submit(fn, it): i for i, it in enumerate(items)}
        pending = set(futs)
        hedged = False
        while len(results) < len(items):
            done, pending = cf.wait(pending, return_when=cf.FIRST_COMPLETED, timeout=0.01)
            for f in done:
                results.setdefault(futs[f], f.result())
            if not hedged and len(results) >= hedge_after * len(items):
                hedged = True
                for f in list(pending):
                    i = futs[f]
                    if i not in results:
                        g = pool.submit(fn, items[i])
                        futs[g] = i
                        pending.add(g)
    finally:
        # don't wait for the stuck originals; first answer wins (~10% extra cost)
        pool.shutdown(wait=False, cancel_futures=True)
    return [results[i] for i in range(len(items))]


def tsdb_series_count(events: list[dict], tags: tuple[str, ...]) -> int:
    """Each unique tag combination is a new time series in a TSDB."""
    return len({tuple(e.get(t) for t in tags) for e in events})
