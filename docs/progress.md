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
| ch30 | The Art and Science of Vendor Partnerships | 58495 | 0 | NOT YET READ (browser disconnected) |
| ch31 | Instrumentation for Observability Teams | 34320 | 0 | NOT YET READ (browser disconnected) |
| ch32 | Where Do We Go From Here? | 20754 | 0 | NOT YET READ (browser disconnected) |

## Method
- In-page JS: fetch chapter HTML, DOMParser → headings/paragraphs/lists/tables/captions/sidebars, stored in `window.__ch[file]`.
- Inject text into page as `<article><p>` and read with get_page_text (~45k chars/call).
- Figures: open `/files/assets/<image>` in a tab and screenshot.
- Notes: `notes/raw-notes.md` (append per chapter); summaries: `docs/chapters/oe2/chapter-NN-summary.md`.

## Outputs (confirmed 2026-11-26)
- Interactive, interview-focused course page (artifact) + runnable POCs. User asked for more interview focus and practical, less theory.
- Repo: phaniuk111/obserability-engineering (cloned at /home/claude/obserability-engineering).
- Supporting docs kept lean: raw notes, synthesis data, generated docs.

## Artifacts
- Course page (private artifact): https://claude.ai/artifact/VvSM4vnGatp4ghNCHhxH5y (slug ea35ec1c-c709-465b-87b1-97eecdd6a9b8, version 1795731588-23f2). Files: course/site/index.html, course.json, diagrams.js.
- POCs: pocs/01..10 (73 tests), pocs/otel/gateway-collector.yaml, pocs/terraform/telemetry_archive/main.tf (not terraform-validated: no terraform binary here).
- Docs: docs/executive-summary.md, knowledge-map.md, requirements.md, claims.md, chapters/oe2/chapter-NN-summary.md.

## Rebuild commands
- python3 course/build.py  (content in course/content/p1..p6.py, synthesis.py, gapfill.py; diagrams in course/diagrams.py)
- pocs/run_all_tests.sh
- NODE_PATH=/path/to/node_modules node course/test_page.js  (jsdom 24)
- python3 course/screenshots.py  (playwright + /usr/bin/google-chrome; output build/tmp/shots, gitignored)
- python3 course/gap_check.py
- Republish: publish_files with slug above, mode patch, base_version = last version.

## Open items
- Read ch30, ch31, ch32 when the Chrome side panel reconnects (book tab id 1648546696; figure tab 1648546764 opened by me, close it at the end).
- Restore the user's book tab (it was replaced with injected text; navigate back to https://learning.oreilly.com/library/view/observability-engineering-2nd/9781098179915/) and close the figure tab I opened (id 1648546764). Not done: browser disconnected.
- After ch30-32: add lessons to course/content/p6.py (replace UNREAD), notes, rerun build + gap check + tests, republish, push.
- Figure coverage: ch1, ch5, ch6 (3 of 7), ch7, ch8 (2 of 3), ch10, ch12 (5 of 12), ch13 (3 of 6), ch14 (3 of 25) viewed. Other figures were judged from captions and surrounding text only (ch15, ch16, ch17, ch20, ch22, ch24, ch25, ch29 figures not opened).

## Log
- 2026-11-26: Pass 0. Spine fetched (47 entries, 32 chapters). All chapter files return 200. Progress file created.
- 2026-11-26: Pass 1. Read preface, foreword, ch1–ch29 in full via injected text + get_page_text; key figures screenshotted. Notes in notes/raw-notes.md. Browser side panel disconnected at ch30.
- 2026-11-26: Built 10 POCs (73 tests pass), OTel gateway config, Terraform example. Pushed.
- 2026-11-26: Built course (29 lessons, 13 SVG diagrams, 18 drills + 29 practice Qs, 63 quiz checks, flashcards, map, checklist, numbers). jsdom 55/55 checks; screenshots light/dark/390px; no overflow, no page errors. Published artifact.
- 2026-11-26: Pass 4 gap check: 180 misses → reviewed by hand → 13 lessons got gap-fill items (course/content/gapfill.py) → 128 remaining are names already described in words, code identifiers or bylines. Reverse check: no course number absent from notes except my own hypotheticals/quiz distractors. Republished.
