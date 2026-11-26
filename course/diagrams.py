"""Inline SVG diagrams (own layout; captions credit the book figure they follow).
Styled by page CSS classes: .d-box .d-acc .d-pink .d-line .d-arrow .d-t .d-s"""
from html import escape


def _txt(x, y, s, cls="d-t", anchor="middle"):
    lines = s.split("\n")
    out = []
    for i, ln in enumerate(lines):
        dy = (i - (len(lines) - 1) / 2) * 16
        out.append(f'<text class="{cls}" x="{x}" y="{y + dy + 5:.0f}" text-anchor="{anchor}">{escape(ln)}</text>')
    return "".join(out)


def box(x, y, w, h, label, cls="d-box", tcls="d-t"):
    return f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>' + _txt(x + w / 2, y + h / 2, label, tcls)


def arrow(x1, y1, x2, y2, label=None, lx=None, ly=None):
    s = f'<line class="d-arrow" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#ah)"/>'
    if label:
        s += _txt(lx if lx is not None else (x1 + x2) / 2, ly if ly is not None else (y1 + y2) / 2 - 10, label, "d-s")
    return s


def svg(h, body, w=720, title=""):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}" xmlns="http://www.w3.org/2000/svg">'
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            '<path d="M0 0L10 5L0 10z" class="d-head"/></marker></defs>' + body + "</svg>")


D = {}

D["pillars_vs_unified"] = dict(caption="Three silos vs one wide event store. Redrawn after Figures 1-1 and 1-5.", svg=svg(250,
    _txt(180, 22, "Three pillars", "d-h") + _txt(540, 22, "Unified model", "d-h")
    + box(20, 50, 100, 60, "Metrics\nTSDB") + box(130, 50, 100, 60, "Logs\naggregator") + box(240, 50, 100, 60, "Traces\ntracer")
    + _txt(180, 150, "correlate by hand,\npay to store 3+ times", "d-s")
    + '<line class="d-line" x1="360" y1="40" x2="360" y2="230"/>'
    + box(400, 50, 280, 70, "One wide event per unit of work\n(or span) in a columnar store", "d-acc")
    + arrow(540, 120, 540, 160) + box(400, 165, 280, 55, "Derive metrics, logs, traces\nat read time", "d-pink"),
    title="Three pillars versus unified storage"))

D["flywheel"] = dict(caption="The test-in-prod flywheel: practice 0 feeds every other practice (ch2).", svg=svg(300,
    box(260, 120, 200, 60, "0 Rich data +\nprecision tooling", "d-acc")
    + box(270, 15, 180, 48, "1 Dev ↔ prod loop") + box(520, 75, 180, 48, "2 Test before deploy")
    + box(520, 185, 180, 48, "3 Instrument +\nvalidate in prod") + box(270, 240, 180, 48, "4 Flags: deploy ≠ release")
    + box(20, 130, 200, 48, "5 Progressive delivery\n+ auto rollback", "d-pink")
    + arrow(450, 40, 560, 74) + arrow(610, 124, 610, 184) + arrow(520, 230, 452, 258) + arrow(270, 262, 170, 180) + arrow(130, 129, 268, 42)
    + arrow(360, 120, 360, 66) + arrow(360, 180, 360, 238),
    title="Flywheel of practices 0 to 5"))

D["trace_waterfall"] = dict(caption="A checkout trace as a waterfall; numbers from the ch1 example (Figure 1-4).", svg=svg(230, "".join(
    _txt(150, 34 + i * 30, n, "d-s", "end")
    + f'<rect class="{c}" x="{170 + s * 3.4:.0f}" y="{22 + i * 30}" width="{d * 3.4:.0f}" height="20" rx="4"/>'
    + _txt(178 + (s + d) * 3.4, 32 + i * 30, f"{d} ms", "d-s", "start")
    for i, (n, s, d, c) in enumerate([("GET /api/checkout", 0, 142, "d-box"), ("auth.verify_token", 2, 12, "d-pink"),
                                       ("db.query_cart", 16, 89, "d-acc"), ("  db.connect", 16, 10, "d-pink"),
                                       ("  db.execute", 27, 79, "d-acc"), ("cache.get_pricing", 106, 13, "d-pink"),
                                       ("render.checkout_page", 119, 23, "d-box")])),
    title="Trace waterfall"))

D["analysis_loop"] = dict(caption="The core analysis loop. Redrawn after Figure 8-1.", svg=svg(280,
    box(250, 15, 220, 52, "1 What are you\ntrying to understand?") + box(480, 112, 220, 56, "2 Visualise; find the\nchange in the curve")
    + box(250, 210, 220, 56, "3 Diff anomaly vs baseline\nacross all dimensions", "d-acc") + box(20, 112, 220, 56, "4 Explained? If not,\nfilter and go again", "d-pink")
    + arrow(470, 45, 560, 110) + arrow(590, 168, 472, 230) + arrow(250, 240, 150, 170) + arrow(140, 112, 248, 50)
    + _txt(360, 140, "automate step 3", "d-s"),
    title="Core analysis loop"))

D["context_layers"] = dict(caption="What an observability agent needs to know. Redrawn after Figure 10-2.", svg=svg(250,
    "".join(box(10 + i * 118, 15, 110, 52, t, "d-pink") for i, t in enumerate(["Business\ncontext", "Service\ntopology", "Naming &\naliases", "Deploy\ncontext", "Known\nissues", "Recent\nincidents"]))
    + arrow(360, 70, 360, 100) + box(230, 102, 260, 44, "Context available?", "d-box")
    + arrow(300, 146, 170, 185, "poor", 220, 160) + arrow(420, 146, 550, 185, "rich", 500, 160)
    + box(40, 188, 260, 48, "generic queries → shallow,\nconfident, wrong") + box(420, 188, 260, 48, "targeted queries →\naccurate diagnosis", "d-acc"),
    title="Agent context layers"))

D["burn"] = dict(caption="Predictive burn alert: project a baseline window forward (≤4x) before the budget empties (ch12).", svg=svg(260,
    '<line class="d-line" x1="60" y1="220" x2="690" y2="220"/><line class="d-line" x1="60" y1="20" x2="60" y2="220"/>'
    + _txt(40, 30, "100%", "d-s", "end") + _txt(40, 220, "0", "d-s", "end") + _txt(375, 246, "time (sliding 30-day window)", "d-s")
    + '<polyline class="d-curve" points="60,40 160,60 230,70 300,95 370,110 420,118"/>'
    + '<line class="d-dash" x1="420" y1="118" x2="640" y2="220"/>'
    + '<rect class="d-pinkf" x="370" y="30" width="50" height="190"/>' + _txt(395, 50, "baseline", "d-s")
    + '<rect class="d-accf" x="420" y="30" width="200" height="190"/>' + _txt(520, 50, "lookahead = 4 × baseline", "d-s")
    + _txt(560, 150, "budget exhausted → page", "d-s"),
    title="Burn alert projection"))

D["retriever"] = dict(caption="Retriever-style storage and query path (ch13).", svg=svg(270,
    box(10, 20, 120, 50, "Receivers\n(stateless)") + arrow(130, 45, 170, 45) + box(172, 20, 110, 50, "Kafka\npartitions") + arrow(282, 45, 320, 45)
    + box(322, 20, 140, 50, "Indexers write\ntime segments", "d-acc") + arrow(462, 45, 500, 45) + box(502, 20, 200, 50, "Segment = 1 file per column\n(+ ts index), dict-encoded")
    + arrow(600, 70, 600, 110) + box(500, 112, 200, 46, "Closed segments → S3", "d-pink")
    + box(10, 190, 150, 54, "Query: prune by\nsegment min/max ts") + arrow(160, 217, 200, 217)
    + box(202, 190, 160, 54, "Fan out: scan only\nreferenced columns", "d-acc") + arrow(362, 217, 402, 217)
    + box(404, 190, 140, 54, "Aggregate per\nsegment") + arrow(544, 217, 580, 217) + box(582, 190, 120, 54, "Merge →\ntop K", "d-pink")
    + _txt(282, 170, "slowest 10% re-issued", "d-s"),
    title="Retriever storage and query"))

D["pipeline"] = dict(caption="Telemetry pipeline stages with resilience and control underneath. Redrawn after Figure 16-1.", svg=svg(230,
    "".join(box(10 + i * 142, 30, 128, 56, t, "d-acc" if i in (1, 3) else "d-box") + (arrow(138 + i * 142, 58, 150 + i * 142, 58) if i < 4 else "")
            for i, t in enumerate(["Collect", "Normalize\n+ secure (PII)", "Enrich", "Reduce\n(filter, sample)", "Route\n(fan-out)"]))
    + box(10, 120, 696, 40, "Data resilience: buffers, disk queues, retries with backoff, backpressure, HA", "d-pink")
    + box(10, 172, 696, 40, "Control plane: visibility, policy, runtime config, fleet management (OpAMP)", "d-box"),
    title="Telemetry pipeline"))

D["sandwich"] = dict(caption="The AI sandwich: deterministic logic validates every AI proposal (ch17).", svg=svg(250,
    box(20, 20, 210, 56, "IntervalSeries + Tariff\n→ BillSet (deterministic)") + arrow(230, 48, 270, 48)
    + box(272, 20, 180, 56, "LLM proposes\nActionPlan", "d-pink") + arrow(452, 48, 492, 48)
    + box(494, 20, 210, 56, "Simulate plan through\ndeterministic engine", "d-acc")
    + arrow(600, 76, 600, 118) + box(470, 120, 240, 52, "Invariants hold and\nsavings reproduce?")
    + arrow(530, 172, 400, 205, "no", 450, 182) + arrow(650, 172, 650, 200, "yes", 670, 188)
    + box(170, 198, 230, 44, "reject + log reason → eval", "d-pink") + box(560, 202, 150, 40, "show user", "d-acc"),
    title="AI sandwich"))

D["ci_dag"] = dict(caption="A CI workflow as a trace: only the critical path matters (ch18).", svg=svg(230,
    box(10, 90, 110, 50, "prebuild\nimage") + arrow(120, 115, 180, 40) + arrow(120, 115, 180, 115) + arrow(120, 115, 180, 190)
    + box(182, 18, 150, 44, "React 2 min") + box(182, 93, 240, 44, "Go 4 min (got slower)") + box(182, 168, 500, 44, "Rust 9 min = critical path", "d-acc")
    + _txt(560, 60, "speeding up Go changes nothing", "d-s"),
    title="CI DAG critical path"))

D["loops"] = dict(caption="Amplifying vs balancing feedback loops (ch24).", svg=svg(240,
    _txt(180, 22, "Amplifying: confidence loop", "d-h") + _txt(540, 22, "Balancing: cost regulation", "d-h")
    + box(100, 40, 160, 40, "Precise signal", "d-acc") + box(200, 110, 150, 40, "Deploy more,\nsmaller") + box(20, 110, 150, 40, "Faster fixes,\nmore trust")
    + box(100, 180, 160, 40, "Lower MTTR", "d-pink") + arrow(240, 80, 270, 108) + arrow(270, 150, 230, 180) + arrow(130, 180, 95, 152) + arrow(95, 108, 125, 82)
    + '<line class="d-line" x1="360" y1="40" x2="360" y2="225"/>'
    + box(450, 40, 180, 40, "Spend visible per team", "d-acc") + box(390, 120, 140, 50, "Too high →\nsample/trim") + box(560, 120, 140, 50, "Blind spots →\ninstrument more")
    + arrow(500, 82, 470, 118) + arrow(580, 82, 620, 118) + arrow(470, 172, 530, 215) + arrow(630, 172, 590, 215) + _txt(540, 228, "equilibrium", "d-s"),
    title="Feedback loops"))

D["dev_ops_loops"] = dict(caption="Dev loop stops at merge, ops loop starts at an alert; the missing loop connects them. After Figures 25-1, 25-2, 25-5.", svg=svg(240,
    box(10, 30, 210, 50, "Dev loop: build → test\n→ merge → move on") + box(500, 30, 210, 50, "Ops loop: alert →\ninvestigate → fix")
    + box(205, 140, 310, 70, "Missing loop: deploy → observe\nyour change → learn → next build", "d-acc")
    + arrow(115, 80, 230, 138) + arrow(490, 138, 605, 80) + _txt(360, 50, "gap: weeks, customer tickets", "d-s"),
    title="Dev ops and missing loop"))

D["build_buy"] = dict(caption="Build vs buy 2×2 (Rick Clark). Redrawn after Figure 29-1.", svg=svg(300,
    '<line class="d-line" x1="80" y1="20" x2="80" y2="270"/><line class="d-line" x1="80" y1="270" x2="700" y2="270"/>'
    + _txt(390, 292, "business value → differentiator", "d-s") + _txt(40, 40, "bespoke", "d-s") + _txt(40, 260, "commodity", "d-s")
    + box(90, 25, 295, 115, "Should not exist\n(low value, bespoke)", "d-pink") + box(395, 25, 300, 115, "Build\n(differentiator, bespoke)", "d-acc")
    + box(90, 150, 295, 115, "Buy\n(commodity, low value):\nobservability platforms", "d-box") + box(395, 150, 300, 115, "Decide\n(commodity, high value)", "d-box"),
    title="Build versus buy"))
