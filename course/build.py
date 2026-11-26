#!/usr/bin/env python3
"""Build course/site/course.json and docs/*.md from course/content/*.

Usage: python3 course/build.py
"""
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "content"))

import p1, p2, p3, p4, p5, p6  # noqa: E402
from synthesis import DRILLS, KNOWLEDGE_MAP, REQUIREMENTS  # noqa: E402
from diagrams import D  # noqa: E402

PARTS = {1: "Introduction to observability", 2: "Instrumentation fundamentals", 3: "Analysis workflows",
         4: "Technical deep dives", 5: "Use cases", 6: "Governance"}
BOOK = "Observability Engineering, 2nd Edition (Majors, Fong-Jones, Miranda, with Parker; O'Reilly 2026)"

import gapfill  # noqa: E402

lessons = p1.LESSONS + p2.LESSONS + p3.LESSONS + p4.LESSONS + p5.LESSONS + p6.LESSONS
_by = {l["id"]: l for l in lessons}
for src, key in ((gapfill.DEEPER, "deeper"), (gapfill.NAMES, "names"), (gapfill.NUMBERS, "numbers"),
                 (gapfill.CHECKS, "checks"), (gapfill.TERMS, "terms")):
    for cid, items in src.items():
        _by[cid][key] = _by[cid][key] + items
unread = p6.UNREAD
ids = [l["id"] for l in lessons]
assert len(ids) == len(set(ids)), "duplicate lesson ids"

# ---------------------------------------------------------------- cross-links
concept_chapters = []
for theme, concepts in KNOWLEDGE_MAP:
    for name, _defn, chs, poc in concepts:
        concept_chapters.append((name, chs))
related = defaultdict(lambda: defaultdict(set))
for name, chs in concept_chapters:
    for a in chs:
        for b in chs:
            if a != b:
                related[a][name].add(b)
for l in lessons:
    l["related"] = [{"concept": c, "chapters": sorted(v)} for c, v in sorted(related[l["id"]].items())]
    l["coverage"] = "Read in full from the book; text paraphrased."
    if l.get("diagram"):
        assert l["diagram"] in D, l["diagram"]
    for c in l["checks"]:
        assert 0 <= c["a"] < len(c["o"])

data = {
    "book": BOOK,
    "parts": PARTS,
    "lessons": lessons,
    "unread": unread,
    "map": [{"theme": t, "concepts": [{"name": n, "def": d, "chapters": c, "poc": p} for n, d, c, p in cs]}
            for t, cs in KNOWLEDGE_MAP],
    "requirements": [{"id": i, "text": t, "source": s, "poc": p} for i, t, s, p in REQUIREMENTS],
    "drills": [{"q": q, "a": a, "source": s} for q, a, s in DRILLS],
}
site = os.path.join(ROOT, "site")
os.makedirs(site, exist_ok=True)
with open(os.path.join(site, "course.json"), "w") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
# Diagrams are our own SVG markup, so they ship as code, not as data.
with open(os.path.join(site, "diagrams.js"), "w") as f:
    f.write("window.DIAGRAMS=" + json.dumps(D, ensure_ascii=False) + ";\n")

# ---------------------------------------------------------------- docs
docs = os.path.join(REPO, "docs")
chdir = os.path.join(docs, "chapters", "oe2")
os.makedirs(chdir, exist_ok=True)


def md_table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]
    return "\n".join(out)


for l in lessons:
    n = l["id"][2:]
    body = [f"# Chapter {int(n)}: {l['title']}", "", f"Part {l['part']}: {PARTS[l['part']]}. Coverage: {l['coverage']}", "",
            "## Summary", "", *[p + "\n" for p in l["picture"]], "## Key ideas", "", *[f"- {d}" for d in l["deeper"]], "",
            "## You will learn", "", *[f"- {x}" for x in l["learn"]], "", "## Claims and numbers", "",
            md_table(l["numbers"], ["Figure", "Context"]), "", "## Terms", "", md_table(l["terms"], ["Term", "Meaning"]), "",
            "## Names to recognise", "", md_table(l["names"], ["Name", "What it is", "Nearest AWS"]), "",
            "## Interview line", "", f"> {l['interview']}", "", "## AWS mapping", "", *[f"- {a}" for a in l["aws"]], "",
            "## Practice question", "", f"**Q.** {l['practice']['q']}", "", f"**Model answer.** {l['practice']['a']}", "",
            "## Exercise", "", l["exercise"], "", "## Takeaways", "", *[f"- {t}" for t in l["takeaways"]], ""]
    with open(os.path.join(chdir, f"chapter-{n}-summary.md"), "w") as f:
        f.write("\n".join(body))
for u in unread:
    n = u["id"][2:]
    with open(os.path.join(chdir, f"chapter-{n}-summary.md"), "w") as f:
        f.write(f"# Chapter {int(n)}: {u['title']}\n\nNot yet read: the browser session disconnected before this chapter. See docs/progress.md.\n")

with open(os.path.join(docs, "knowledge-map.md"), "w") as f:
    f.write("# Knowledge map\n\nThemes → concepts → one-line definition → chapters → POC.\n\n")
    for t in data["map"]:
        f.write(f"## {t['theme']}\n\n")
        f.write(md_table([[c["name"], c["def"], ", ".join(c["chapters"]), c["poc"] or "—"] for c in t["concepts"]],
                         ["Concept", "Definition", "Chapters", "POC"]) + "\n\n")

with open(os.path.join(docs, "requirements.md"), "w") as f:
    f.write("# Requirements checklist\n\nWhat the book says a system or team should have in place. Use it as an assessment: tick what you can show evidence for.\n\n")
    f.write(md_table([[r["id"], r["text"], r["source"], r["poc"]] for r in data["requirements"]], ["#", "Requirement", "Source", "POC"]) + "\n")

with open(os.path.join(docs, "claims.md"), "w") as f:
    f.write("# Numbers to know\n\nCheck the book before quoting any figure in writing. Figures are as reported by the book (often from contributors, Gartner, or the authors' own systems).\n\n")
    f.write("## Curated\n\n" + md_table([
        ["99.9% budget", "43m50s/month; 8h45m57s/year (365.25-day year)", "ch12"],
        ["99.99% budget", "≈4.38 min/month", "ch12"],
        ["Relative burn example", "10M req, 99.9%, 15-min windows → ~3.4 allowed; 4x ≈ 13, 20x ≈ 68 (exact 13.9 / 69.4)", "ch12"],
        ["Dimensionality", "4 fields → 15 combos; 8 → 255; 30 → ~1.1B", "ch1"],
        ["Average of averages", "183 ms naive vs ~175 ms weighted", "ch5"],
        ["Spend", "20–30% of infra (ch3/ch23); 10–25% of infra bill and 2nd after cloud (ch27, Gartner); up to a third (ch25)", "ch3, ch23, ch25, ch27"],
        ["Gartner customer", "$50k (2009) → $24M (2024), 48%/yr for 15 years", "ch23, ch29"],
        ["Retriever scale", "1.5 PB, >1B segments, 3–5M spans/s, 50 ms median / 5 s P99", "ch13"],
        ["ClickHouse node", "32c/128 GB ≈ 20B events/day; 300–400k/s peak; 10–20x compression", "ch14"],
        ["Query Assistant", "25% → ~14% → <1% error rate", "ch21"],
        ["Fin", "~70 deploys/day, 8–15 min each; resolution rate +~1 pt/month; −2 s TTFT", "ch22, ch25"],
        ["Honeycomb builds", "<15 min SLO (≤5% over); 7→14 min regression; target <7 min", "ch18"],
    ], ["Topic", "Figure", "Chapter"]) + "\n\n## Per chapter\n\n")
    for l in lessons:
        f.write(f"### {l['id']} {l['title']}\n\n" + md_table(l["numbers"], ["Figure", "Context"]) + "\n\n")

EXEC = f"""# Executive summary

*{BOOK}* argues that observability is a property of dependable software: how well you can explain any system state, including ones you've never seen, from the telemetry you already have. Its central technical claim is that wide, structured, high-cardinality events, stored once in a columnar store and aggregated at read time, beat the three pillars (separate metrics, logs and traces) for code you write. The three pillars stay right for infrastructure (ch1, ch3, ch25).

## Main arguments

1. **Unify the data.** Metrics, logs and traces are all structured events. Capture one wide event per unit of work and derive the rest when you need it (ch5, ch6). Pre-aggregation is a one-way trip (ch1).
2. **Instrument deliberately with OpenTelemetry.** Combine auto and custom instrumentation, create spans only for interesting and aggregable work, layer signals, and keep naming consistent with schemas (ch4, ch7).
3. **Analyse from first principles.** The core analysis loop, automated as baseline-vs-anomaly diffing, lets any engineer debug unfamiliar systems (ch8). Observability is the telescope that aims the debugger (ch9).
4. **Alert on user pain.** Event-based SLIs and predictive burn alerts replace threshold alert fatigue (ch11, ch12).
5. **The data platform is solvable.** Time-partitioned columnar storage (Retriever, ClickHouse), sampling with recorded rates, and telemetry pipelines make it affordable (ch13–ch16).
6. **Context is everything for AI.** Agents need an explicit context layer. AI outputs need deterministic invariants. LLM features need evals fed by telemetry (ch10, ch17, ch21).
7. **Learning speed is the constraint.** With AI, generating code is cheap and validating it is not. Observability is the sensing part of every delivery feedback loop. Run it as a platform product and an investment, not a cost center (ch23–ch29).

## Where the parts meet

The same idea repeats at every level. A precise, context-rich signal closes a feedback loop: a deploy (ch2), a canary (ch2), an SLO burn (ch12), a CI build (ch18), a mobile cohort (ch19), an LLM eval (ch21), Fin's latency and cost (ch22), and the organisation's own learning (ch24, ch25).

## Turning this into interview answers

Lead with an outcome, name the mechanism, give one number. Example: "Event-based SLIs: a minute where 6% of requests are slow burns 6% of budget, not 100%, which matters at four nines where the month's budget is about 4.4 minutes." The course page has an interview line per chapter and a drill bank.

## Not covered

Chapters 30–32 (vendor partnerships, instrumentation for observability teams, where we go from here) were not read: the browser session disconnected. Some figures in Part IV/V were checked from captions only, without viewing the image (noted in docs/progress.md).
"""
with open(os.path.join(docs, "executive-summary.md"), "w") as f:
    f.write(EXEC)

print(f"lessons={len(lessons)} unread={len(unread)} diagrams={len(D)} drills={len(DRILLS)} reqs={len(REQUIREMENTS)}")
print("course.json bytes:", os.path.getsize(os.path.join(site, "course.json")))
