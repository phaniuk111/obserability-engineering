"""POC 8: ontologies, invariants and the AI sandwich (book ch17), plus LLM
telemetry habits from ch21 (cost derived at query time, harness repairs,
eval promotion).

Deterministic core: IntervalSeries + Tariff -> BillSet, guarded by three
invariants (coverage, arithmetic, determinism). An "AI" proposes an
ActionPlan; we never execute it, we simulate it through the deterministic
core and reject hallucinated savings. Every step emits the same payload in
CI and production (signal parity).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Window:
    start_h: int  # inclusive, 0-23
    end_h: int    # exclusive, may wrap past midnight
    rate: float   # $ per kWh

    def covers(self, h: int) -> bool:
        return self.start_h <= h < self.end_h if self.start_h < self.end_h else (h >= self.start_h or h < self.end_h)


@dataclass(frozen=True)
class Tariff:
    tariff_id: str
    ruleset_version: str
    windows: tuple[Window, ...]


@dataclass(frozen=True)
class IntervalSeries:
    series_id: str
    usage_kwh: tuple[float, ...]  # one value per hour of day
    lineage: dict = field(default_factory=lambda: {"source": "smart_meter_api"})


class InvariantViolation(Exception):
    def __init__(self, invariant: str, detail: str):
        super().__init__(f"{invariant}: {detail}")
        self.invariant = invariant


def price(series: IntervalSeries, tariff: Tariff) -> dict:
    lines = []
    for h, kwh in enumerate(series.usage_kwh):
        matches = [w for w in tariff.windows if w.covers(h % 24)]
        if len(matches) != 1:  # coverage: exactly one window per interval
            raise InvariantViolation("coverage", f"hour {h} matched {len(matches)} windows")
        lines.append(round(kwh * matches[0].rate, 4))
    total = round(sum(lines), 2)
    if abs(total - sum(lines)) > 0.01:  # arithmetic: whole == sum of parts within $0.01
        raise InvariantViolation("arithmetic", "total != sum(lines)")
    payload = json.dumps([series.series_id, tariff.tariff_id, tariff.ruleset_version, lines], sort_keys=True)
    return {"input_series_id": series.series_id, "applied_tariff_id": tariff.tariff_id,
            "ruleset_version": tariff.ruleset_version, "total_cost": total, "lines": lines,
            "pricing_coverage": 1.0, "determinism_hash": hashlib.sha256(payload.encode()).hexdigest()[:16]}


def apply_plan(series: IntervalSeries, plan: dict) -> IntervalSeries:
    """Counterfactual series: move a device's kWh from one hour to another."""
    usage = list(series.usage_kwh)
    for a in plan["actions"]:
        frm, to, kwh = a["from_h"], a["to_h"], a["kwh"]
        if not (0 <= frm < len(usage) and 0 <= to < len(usage)):
            raise InvariantViolation("coverage", f"hour out of range in plan {plan['plan_id']}")
        if usage[frm] < kwh:
            raise InvariantViolation("physics", f"cannot move {kwh} kWh from hour {frm}")
        usage[frm] -= kwh
        usage[to] += kwh
    return IntervalSeries(series.series_id + ":cf:" + plan["plan_id"], tuple(usage), {"derived_from": series.series_id})


def validate_plan(series: IntervalSeries, tariff: Tariff, plan: dict, tolerance=0.5, confidence_floor=0.6) -> dict:
    """The sandwich: deterministic -> AI proposal -> deterministic check.
    Returns the universal payload whether accepted or rejected."""
    event = {"plan_id": plan["plan_id"], "series_id": series.series_id, "tariff_id": tariff.tariff_id,
             "ruleset_version": tariff.ruleset_version, "model_name": plan.get("model_name"),
             "prompt_version": plan.get("prompt_version"),
             "predicted_delta_usd": plan["predicted"]["bill_delta_usd"]}
    if plan.get("confidence", 1.0) < confidence_floor:
        return {**event, "proposal_status": "rejected", "rejection_reason": "low_confidence"}
    try:
        base = price(series, tariff)
        cf = price(apply_plan(series, plan), tariff)
    except InvariantViolation as v:
        return {**event, "proposal_status": "rejected", "rejection_reason": f"invariant_{v.invariant}"}
    actual = round(cf["total_cost"] - base["total_cost"], 2)
    event["simulated_delta_usd"] = actual
    if abs(actual - plan["predicted"]["bill_delta_usd"]) > tolerance:
        return {**event, "proposal_status": "rejected", "rejection_reason": "simulation_mismatch"}
    return {**event, "proposal_status": "accepted"}


def rejection_rate(events: list[dict]) -> float:
    """Highest-fidelity AI reliability signal (ch17)."""
    return sum(e["proposal_status"] == "rejected" for e in events) / len(events)


# ------------------------------------------------------------ ch21 helpers
PRICES_PER_MTOK = {"model-a": (3.0, 15.0), "model-b": (0.25, 1.25)}  # (input, output) $/1M tokens, illustrative


def cost_at_query_time(span: dict) -> float:
    """Don't store cost on the span; derive it from model + token counts so you
    can reprice history when prices or models change."""
    pin, pout = PRICES_PER_MTOK[span["gen_ai.request.model"]]
    return (span["gen_ai.usage.input_tokens"] * pin + span["gen_ai.usage.output_tokens"] * pout) / 1e6


def repair_query(q: dict) -> tuple[dict, bool]:
    """Harness fix from Query Assistant: COUNT takes no column -> drop it."""
    fixed, changed = json.loads(json.dumps(q)), False
    for c in fixed.get("calculations", []):
        if c.get("op") == "COUNT" and "column" in c:
            del c["column"]
            changed = True
    return fixed, changed


def promote_to_eval(trace: dict, ideal_output: dict | None = None) -> dict:
    """Production trace -> golden dataset row (inputs, output, expected)."""
    return {"input": trace["input"], "observed_output": trace["output"],
            "expected": ideal_output if ideal_output is not None else trace["output"],
            "source_trace_id": trace["trace_id"], "feedback": trace.get("user_feedback")}
