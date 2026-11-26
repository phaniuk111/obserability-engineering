# Observability Engineering (2nd ed.): interview-focused study kit

A study kit built from a chapter-by-chapter read of *Observability Engineering, 2nd Edition* (Majors, Fong-Jones, Miranda, with Parker; O'Reilly 2026). Everything is paraphrased; nothing reproduces the book's text.

**Coverage:** preface, foreword and chapters 1–29 read in full. Chapters 30–32 aren't read yet: the browser session ended before them. See `docs/progress.md`.

## What's here

| Path | What |
|---|---|
| `course/` | Interactive course: one lesson per chapter (idea, interview line, AWS mapping, practice Q + model answer, checks), plus interview drills, quiz, flashcards, knowledge map, checklist and numbers. Published as a private claude.ai artifact. |
| `pocs/` | 10 runnable POCs (Python stdlib, 73 tests): wide events, a tracer, BubbleUp, SLO burn alerts, sampling, a columnar store, a telemetry pipeline, the AI sandwich, cost/CI maths, mobile ring buffer. Plus an OTel gateway config and Terraform. |
| `docs/` | Executive summary, knowledge map, requirements checklist, numbers to know, per-chapter summaries, progress log. Generated from the same data as the course. |
| `notes/raw-notes.md` | Detailed reading notes per chapter (paraphrased). |

## Rebuild and verify

```bash
python3 course/build.py                 # course/site/course.json, diagrams.js and docs/*.md
pocs/run_all_tests.sh                   # 73 POC tests
NODE_PATH=<dir with jsdom> node course/test_page.js   # 55 page checks in jsdom
python3 course/screenshots.py           # light/dark/phone screenshots (playwright + Chrome)
python3 course/gap_check.py             # notes vs course gap report
```

Check the book before quoting any number in writing (`docs/claims.md`).
