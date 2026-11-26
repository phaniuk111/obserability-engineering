"""POC 3: automate the brute-force part of the core analysis loop (book ch8).

Select the anomalous events (e.g. the slow ones you boxed on a heatmap),
compare every dimension's value distribution against the baseline, and rank
by how over-represented each value is in the selection. This is the idea
behind Honeycomb's BubbleUp; nothing here needs to know about your app.
"""
from __future__ import annotations

from collections import Counter
from typing import Callable, Iterable

IGNORE = {"ts", "duration_ms", "trace.trace_id", "trace.span_id", "trace.parent_id", "main", "name"}


def _freq(events: list[dict], key: str) -> Counter:
    return Counter(str(e.get(key)) for e in events)


def bubble_up(events: Iterable[dict], selected: Callable[[dict], bool], top: int = 10,
              max_cardinality: int = 1000, min_selection_share: float = 0.05) -> list[dict]:
    events = list(events)
    sel = [e for e in events if selected(e)]
    base = [e for e in events if not selected(e)]
    if not sel or not base:
        return []
    keys = {k for e in events for k in e} - IGNORE
    findings = []
    for k in keys:
        fs, fb = _freq(sel, k), _freq(base, k)
        if len(fs) + len(fb) > max_cardinality:  # unique IDs never explain a cohort alone
            continue
        for val, n in fs.items():
            s_share, b_share = n / len(sel), fb.get(val, 0) / len(base)
            if s_share < min_selection_share:
                continue
            findings.append({"field": k, "value": val, "selection_pct": round(100 * s_share, 1),
                             "baseline_pct": round(100 * b_share, 1),
                             "score": round(s_share - b_share, 4)})
    return sorted(findings, key=lambda f: -f["score"])[:top]


def core_analysis_loop(events: list[dict], is_anomalous: Callable[[dict], bool], rounds: int = 3) -> list[dict]:
    """Iterate: diff, take the strongest dimension, filter to it, repeat (ch8 step 4)."""
    explanation, scope = [], events
    for _ in range(rounds):
        top = bubble_up(scope, is_anomalous, top=1)
        if not top or top[0]["score"] < 0.2:
            break
        f = top[0]
        explanation.append(f)
        scope = [e for e in scope if str(e.get(f["field"])) == f["value"]]
    return explanation
