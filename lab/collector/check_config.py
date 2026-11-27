"""Structural lint for Collector configs (local.yaml and production/*.yaml).

This is NOT `otelcol validate`: it cannot know whether a component accepts a given key.
It catches the mistakes that are easy to make by hand: a processor defined but used in no
pipeline, a storage extension nobody references, a connector wired on one side only,
tail sampling in the wrong place.

Usage: python3 check_config.py [file ...]      (needs PyYAML)
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = ("receivers", "processors", "exporters", "connectors", "extensions")
CONTEXT_PROCESSORS = ("k8sattributes",)   # must run before anything that regroups spans


def kind(component_id: str) -> str:
    return component_id.split("/", 1)[0]


def lint(cfg: dict) -> list[str]:
    problems = []
    defined = {s: set((cfg.get(s) or {}).keys()) for s in SECTIONS}
    service = cfg.get("service") or {}
    used = {s: set() for s in SECTIONS}
    as_exporter, as_receiver = {}, {}

    for ext in service.get("extensions") or []:
        used["extensions"].add(ext)
        if ext not in defined["extensions"]:
            problems.append(f"service.extensions uses undefined extension {ext}")

    for pid, p in (service.get("pipelines") or {}).items():
        if kind(pid) not in ("traces", "metrics", "logs", "profiles"):
            problems.append(f"pipeline {pid}: unknown signal type")
        for role in ("receivers", "processors", "exporters"):
            if role != "processors" and not p.get(role):
                problems.append(f"pipeline {pid}: no {role}")
            for cid in p.get(role) or []:
                if cid in defined[role]:
                    used[role].add(cid)
                elif role != "processors" and cid in defined["connectors"]:
                    used["connectors"].add(cid)
                    (as_exporter if role == "exporters" else as_receiver).setdefault(cid, []).append(pid)
                else:
                    problems.append(f"pipeline {pid}: {role[:-1]} {cid} is not defined")
        procs = p.get("processors") or []
        if "memory_limiter" in procs and procs[0] != "memory_limiter":
            problems.append(f"pipeline {pid}: memory_limiter should be the first processor")
        ts = [i for i, c in enumerate(procs) if kind(c) == "tail_sampling"]
        if ts:
            late = [c for c in procs[ts[0] + 1:] if kind(c) in CONTEXT_PROCESSORS]
            if late:
                problems.append(f"pipeline {pid}: {late} must run before tail_sampling")
            if any(kind(c) == "spanmetrics" for c in p.get("exporters") or []):
                problems.append(f"pipeline {pid}: spanmetrics after tail_sampling counts only sampled spans")

    for s in SECTIONS:
        for cid in sorted(defined[s] - used[s]):
            problems.append(f"{s[:-1]} {cid} is defined but never used")
    for cid in sorted(used["connectors"]):
        if cid not in as_exporter or cid not in as_receiver:
            problems.append(f"connector {cid} must be an exporter in one pipeline and a receiver in another")
        elif kind(cid) == "forward" and {kind(x) for x in as_exporter[cid]} != {kind(x) for x in as_receiver[cid]}:
            problems.append(f"connector {cid}: forward joins pipelines of one signal type")

    referenced = set()
    for eid, e in (cfg.get("exporters") or {}).items():
        e = e or {}
        for label, ref in (("sending_queue.storage", (e.get("sending_queue") or {}).get("storage")),
                           ("auth.authenticator", (e.get("auth") or {}).get("authenticator"))):
            if ref:
                referenced.add(ref)
                if ref not in used["extensions"]:
                    problems.append(f"exporter {eid}: {label} -> {ref} is not an enabled extension")
    for ext in sorted(used["extensions"]):
        if kind(ext) in ("file_storage", "sigv4auth") and ext not in referenced:
            problems.append(f"extension {ext} is enabled but no exporter references it")
    return problems


def load(path: str) -> dict:
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


def all_configs() -> list[str]:
    return sorted(glob.glob(os.path.join(HERE, "*.yaml")) + glob.glob(os.path.join(HERE, "production", "*.yaml")))


def main(paths: list[str]) -> int:
    bad = 0
    for path in paths or all_configs():
        problems = lint(load(path))
        print(f"{os.path.relpath(path, HERE)}: {'OK' if not problems else str(len(problems)) + ' problem(s)'}")
        for p in problems:
            print("  -", p)
        bad += bool(problems)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
