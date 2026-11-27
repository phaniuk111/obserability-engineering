# Progress: Observability Engineering, 2nd Edition (study kit)

Book: *Observability Engineering, 2nd Edition* (O'Reilly, ISBN 9781098179915)
Source: O'Reilly Learning, read in the user's browser via
`/api/v2/epubs/urn:orm:book:9781098179915/files/<file>.html`

## Structure (32 chapters, 6 parts; all available, status 200)

| File | Title | chars | imgs | Status |
|---|---|---|---|---|
| foreword01 | Foreword | 5082 | 0 | read in full |
| preface01 | Preface | 23619 | 0 | read in full |
| **Part I. Introduction to Observability** |||||
| ch01 | What Is Observability? | 32052 | 6 | read in full |
| ch02 | How Code Crosses Over: Validating Developer Intent in Production | 44304 | 0 | read in full |
| ch03 | The Origins of Observability in Software | 24481 | 0 | read in full |
| **Part II. Instrumentation Fundamentals** |||||
| ch04 | Getting Started with Instrumentation | 31539 | 0 | read in full |
| ch05 | Structured Events Are the Building Blocks of Observability | 39783 | 5 | read in full |
| ch06 | Making Structured Events Arbitrarily Wide | 43219 | 7 | read in full |
| ch07 | Instrumenting Your Code with OpenTelemetry | 45976 | 1 | read in full |
| **Part III. Analysis Workflows** |||||
| ch08 | Getting Started with Observability Analysis | 29895 | 3 | read in full |
| ch09 | Observability-Driven Development | 27824 | 0 | read in full |
| ch10 | The Role of AI Agents for Observability | 24624 | 2 | read in full |
| ch11 | Using Service Level Objectives for Reliability | 45855 | 0 | read in full |
| **Part IV. Observability Technical Deep Dives** |||||
| ch12 | Acting On and Debugging SLO-Based Alerts | 40195 | 12 | read in full |
| ch13 | Efficient Data Storage with Retriever | 54997 | 6 | read in full |
| ch14 | Efficient Data Storage with ClickHouse | 66267 | 25 | read in full |
| ch15 | Cheap and Accurate Enough Sampling | 30277 | 4 | read in full |
| ch16 | Telemetry Management with Pipelines | 30865 | 7 | read in full |
| ch17 | Ontologies as a Shared Language for Humans and AI | 27652 | 3 | read in full |
| **Part V. Observability Use Cases** |||||
| ch18 | Observability for CI/CD Pipelines | 37740 | 0 | read in full |
| ch19 | Observability for Mobile and Frontend | 67378 | 0 | read in full |
| ch20 | Performance Engineering with Observability | 48178 | 5 | read in full |
| ch21 | Observability for Large Language Models | 28909 | 1 | read in full |
| ch22 | Fin's Case Study in Modern Engineering | 17821 | 12 | read in full |
| **Part VI. Observability Governance** |||||
| ch23 | Organizational Learning Speed Is Now Your Biggest Constraint: An Open Letter to CTOs | 38890 | 0 | read in full |
| ch24 | Systems Thinking for Software Delivery | 29275 | 8 | read in full |
| ch25 | The Observability Landscape Through a Systems Lens | 25843 | 9 | read in full |
| ch26 | The Business Case for Observability | 29028 | 0 | read in full |
| ch27 | Diagnosing Your Observability Investment | 13173 | 0 | read in full |
| ch28 | The Organizational Shift | 42242 | 0 | read in full |
| ch29 | Build Versus Buy (Versus Open Source) | 54254 | 3 | read in full |
| ch30 | The Art and Science of Vendor Partnerships | 58495 | 0 | read in full (2026-11-27) |
| ch31 | Instrumentation for Observability Teams | 34320 | 0 | read in full (2026-11-27) |
| ch32 | Where Do We Go From Here? | 20754 | 0 | read in full (2026-11-27) |

## Method
- In-page JS: fetch chapter HTML, DOMParser → headings/paragraphs/lists/tables/captions/sidebars, stored in `window.__ch[file]`.
- Inject text into page as `<article><p>` and read with get_page_text (~45k chars/call).
- Figures: open `/files/assets/<image>` in a tab and screenshot.
- Notes: `notes/raw-notes.md` (append per chapter); summaries: `docs/chapters/oe2/chapter-NN-summary.md`.

## Outputs (confirmed 2026-11-26, revised 2026-11-27)
- Interactive, interview-focused course page (artifact). User asked for more interview focus and practical, less theory.
- 2026-11-27: user said the Python POCs "don't make sense" and chose a real stack that runs locally, to be run by them (I cannot start Docker).
- Repo named by the user: https://github.com/phaniuk111/obserability-engineering

## Artifacts
- Course: https://claude.ai/artifact/VvSM4vnGatp4ghNCHhxH5y (slug ea35ec1c-c709-465b-87b1-97eecdd6a9b8). Files: index.html, course.json, diagrams.js.
- Lab: lab/ (app on the real OTel SDK, docker-compose with Collector, ClickHouse, Prometheus, Jaeger, Grafana; 8 lab guides; smoke-test.sh).
- Production-shaped Collector configs: lab/collector/production/. Terraform: lab/aws/terraform/telemetry_archive/.

## Rebuild commands
- python3 course/build.py                      (course.json, diagrams.js, docs/*.md)
- NODE_PATH=<jsdom dir> node course/test_page.js   (68 page checks)
- cd lab && make test                           (19 tests: real SDK + OTLP + embedded ClickHouse; needs flask, opentelemetry-*, chdb, pyyaml)
- cd lab && make smoke                          (needs Docker; not run by me)
- python3 course/gap_check.py

## Verification status
- Run here: app instrumentation, OTLP export, every SQL file in lab/clickhouse/queries (on chdb), Collector config lint, page tests, screenshots.
- Not run here: docker-compose stack, the Collector itself, Prometheus rules, Grafana provisioning, Terraform validate/apply.
- Numbers in the course were re-checked against chapter text in the browser on 2026-11-27 (22 unmatched tokens, all traced to figures, spelled-out numbers or code blocks).

## Open items
- User to run `make smoke` and report failures (most likely spot: span-metric names in prometheus/rules.yml for the pinned Collector image).
- Some Part IV/V figures were checked from captions only.

## Log
- 2026-11-26: Pass 0. Structure captured from the O'Reilly spine API.
- 2026-11-26: Pass 1. Read preface, foreword, ch1–ch29 in full; key figures viewed. Notes in notes/raw-notes.md.
- 2026-11-26: Built 10 stdlib POCs, a gateway Collector config and a Terraform example; course built, tested, published; gap check folded in. Pushed.
- 2026-11-27: Second pass. Read ch30–32 in full; lessons added. Verified technical claims against official docs (W3C Trace Context, OTel Collector components, semantic conventions, ClickHouse settings, AWS service status); fixes and links in docs/sources.md and per lesson.
- 2026-11-27: Replaced the stdlib POCs with lab/ (real stack) at the user's request. Collector configs rebuilt as two tiers; Terraform tightened.
