# Observability Engineering (2nd edition): study kit

An interview-focused course and a hands-on lab built from *Observability Engineering, 2nd Edition* (Majors, Fong-Jones, Miranda; O'Reilly 2026). Everything is paraphrased; read the book for the original.

| Part | Where | What it is |
|---|---|---|
| Course | https://claude.ai/artifact/VvSM4vnGatp4ghNCHhxH5y, source in `course/` | One lesson per chapter (32), interview lines, practice questions, drills, flashcards, AWS mapping, official-doc links |
| Lab | [`lab/`](lab/README.md) | Three services on the real OpenTelemetry SDK, Collector, ClickHouse, Prometheus, Jaeger, Grafana. Eight labs: tracing, wide events, finding a fault without a hypothesis, SLO burn alerts, sampling, pipeline, storage, production shape |
| Docs | `docs/` | Executive summary, per-chapter summaries, knowledge map, requirements checklist, numbers, [official sources](docs/sources.md) |
| Notes | `notes/raw-notes.md` | Paraphrased reading notes for every chapter |

## Start here

```bash
cd lab
make up            # Docker: starts the stack and prints URLs
make smoke         # checks the stack end to end
make test          # no Docker: real SDK + OTLP + embedded ClickHouse, runs every lab query
```

## Rebuild the course

```bash
python3 course/build.py
NODE_PATH=/path/to/node_modules node course/test_page.js    # needs jsdom
```

## Coverage and limits

- All 32 chapters read in full. Some figures in Parts IV–V were checked from captions only.
- Technical details that age (Collector component names, AWS services, semantic conventions) were checked against official documentation on 2026-11-27; each lesson lists what changed since the book.
- The lab's app, OTLP export and SQL were run and tested. The Docker stack, the Collector configs, Prometheus rules, Grafana provisioning and Terraform were written against the docs and linted, not executed. `lab/README.md` has the table.
