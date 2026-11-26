"""POC 4: SLOs, error budgets and burn alerts (book ch11, ch12).

Covers the exact worked examples from the book so you can reproduce them in
an interview: budget minutes per "nines", event-based SLIs with eligibility,
relative burn (SRE Workbook), short-term linear vs proportional projection,
context-aware projection (port of the book's Go isBurnViolation), and why
time-bucketed SLIs burn budget far faster than event-based ones.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

MINUTES_PER_30D = 30 * 24 * 60
SECONDS_PER_YEAR = 365 * 24 * 3600


def budget_minutes(target: float, period_minutes: int = MINUTES_PER_30D) -> float:
    return (1 - target) * period_minutes


def fmt_duration(seconds: float) -> str:
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s"


# --------------------------------------------------------------- event SLI
SLI = Callable[[dict], Optional[bool]]  # True good, False bad, None = not eligible


def checkout_sli(e: dict) -> Optional[bool]:
    """Mirrors the ch11 expression: POST /checkout, not kube-probe,
    good if status < 400 AND duration <= 4000 ms; ineligible -> None."""
    eligible = (e.get("http.request.method") == "POST" and e.get("http.route") == "/checkout"
                and not str(e.get("user_agent.original", "")).startswith("kube-probe")
                and e.get("trace.parent_id") is None)  # root/server spans only
    if not eligible:
        return None
    return e.get("http.response.status_code", 500) < 400 and e.get("duration_ms", 1e9) <= 4000


def evaluate(events, sli: SLI) -> tuple[int, int]:
    good = bad = 0
    for e in events:
        r = sli(e)
        if r is True:
            good += 1
        elif r is False:
            bad += 1
    return good, bad


# ----------------------------------------------------------- relative burn
def relative_burn_threshold(monthly_requests: int, target: float, window_min: int, factor: float) -> float:
    """Failures allowed in one window at `factor` x the steady burn rate."""
    windows = MINUTES_PER_30D / window_min
    allowed_per_window = monthly_requests * (1 - target) / windows
    return allowed_per_window * factor


# ------------------------------------------------------- short-term burn
def project_linear(fails_in_baseline: int, baseline_h: float, lookahead_h: float) -> float:
    return fails_in_baseline * lookahead_h / baseline_h


def project_proportional(fails: int, total: int, expected_units_in_lookahead: float) -> float:
    """Assume the *rate* continues against normal traffic, not the raw count."""
    return (fails / total) * expected_units_in_lookahead


# --------------------------------------------------- context-aware burn
@dataclass
class SLOConfig:
    time_period_days: int
    budget_ppm: int  # allowed failures per million (99% -> 10_000)


@dataclass
class BurnAlertConfig:
    exhaustion_minutes: int  # lookahead


LOOKBACK_RATIO = 4  # baseline = lookahead / 4 (ch12 "factor of four")


def is_burn_violation(now_min: int, ba: BurnAlertConfig, slo: SLOConfig,
                      timestamps: list[int], total: dict[int, int], fails: dict[int, int]) -> bool:
    """Python port of the book's Go isBurnViolation (times in minutes)."""
    p_offset = ba.exhaustion_minutes // LOOKBACK_RATIO
    p_window = now_min - p_offset
    t_window = now_min - slo.time_period_days * 1440 + ba.exhaustion_minutes
    running_total = running_fails = projected_total = projected_fails = 0
    for t in reversed(timestamps):
        if t < t_window:
            break
        running_total += total[t]
        running_fails += fails[t]
        if t > p_window:
            projected_total += LOOKBACK_RATIO * total[t]
            projected_fails += LOOKBACK_RATIO * fails[t]
    projected_total += running_total
    projected_fails += running_fails
    allowed = projected_total * slo.budget_ppm // 1_000_000
    return projected_fails != 0 and projected_fails >= allowed


def budget_remaining(total: int, fails: int, target: float) -> float:
    allowed = total * (1 - target)
    return 1 - fails / allowed if allowed else 0.0


# -------------------------------------- time-bucketed vs event-based SLIs
def time_based_bad_minutes(minutes: list[list[float]], threshold_ms: float, pct: float = 95) -> int:
    """Each minute is good only if its P{pct} < threshold. One bad minute burns the whole minute."""
    bad = 0
    for reqs in minutes:
        s = sorted(reqs)
        k = max(0, int(round(pct / 100 * len(s))) - 1)
        bad += s[k] >= threshold_ms
    return bad


def event_based_bad_fraction(minutes: list[list[float]], threshold_ms: float) -> float:
    reqs = [r for m in minutes for r in m]
    return sum(r >= threshold_ms for r in reqs) / len(reqs)
