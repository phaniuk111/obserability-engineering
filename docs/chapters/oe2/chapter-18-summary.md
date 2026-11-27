# Chapter 18: Observability for CI/CD

Part 5: Use cases. Coverage: Read in full from the book; text paraphrased.

## Summary

CI/CD is a production system for developer feedback, and it has the best ROI of any observability work. Every request has a developer waiting on it, and volume is small (about a dozen PRs per developer per day at most).

Workflow = trace, job = spans under it, step = span within the job. Add repo and branch. Your first SLIs are end-to-end time to validated, flake rate (success on retry) and test failure rate on main.

Jobs form a DAG. Only the critical path matters: if Rust dominates, speeding up the Go build changes nothing.

## Key ideas

- Experiment instead of guessing: more cores didn't help a webpack build missing ThreadLoaders; Go builds halved with more cores; slow releases were network-bound pushing images to every region from one job.
- Retries hide 5% flakes but inflate the tail: P50 stays flat while P90 doubles. Ephemeral dedicated runners can be cheaper once retries are counted. Watch OS limits and cgroups.
- Use toolchain caches (Go module/build) for incrementality without losing isolation.
- Honeycomb: SLO of no more than 5% of builds over 15 minutes. Median doubled from 7 to 14 minutes (2018–19). PRs per week went from 10–20 to 100+. Amdahl's law bit. Traces showed 3.5 GB gzip-moved between steps, so they switched to a single Docker Bake. BuildKit has native OTel: set TRACEPARENT. Result: under 7 minutes, so developers stay and watch.
- Tools: GitHub Actions OTel receiver/action, Buildkite native OTel, otel-cli exec, DOCKER_CLI_OTEL_EXPORTER_OTLP_ENDPOINT.
- The common complaint, 'the suite takes 5 minutes on my MacBook but 20 in CI', usually means CI starts from scratch every time. Persist the toolchain caches.

## You will learn

- Model CI workflows as traces and find the critical path
- Define CI SLIs and use P50 vs P90 to see retry costs
- Retell the Honeycomb 7-minute build story

## Claims and numbers

| Figure | Context |
|---|---|
| 15 min / 5% | Honeycomb build SLO |
| 7 → 14 min | Median build 2018–19 |
| 10–20 → 100+ | PRs/week 2020–2025 |
| 3.5 GB | Data moved between steps |
| <7 min | Target that keeps devs watching |

## Terms

| Term | Meaning |
|---|---|
| Critical path | Longest dependent chain determining end-to-end time |
| Flake rate | Share of runs passing only on retry |

## Names to recognise

| Name | What it is | Nearest AWS |
|---|---|---|
| Amdahl's law | Serial fraction caps speedup | n/a |
| Docker Bake / BuildKit | Parallel multi-target image builds; native OTel | CodeBuild with BuildKit |
| otel-cli | Wrap shell steps as spans | CodeBuild buildspec |
| CircleCI buildevents | Legacy Honeycomb CI tracing | n/a |

## Interview line

> I trace the pipeline: workflow as a trace, jobs as spans. I find the critical path, set an SLO on time-to-validated, and track flake rate separately so retries don't quietly double the tail.

## AWS mapping

- CodeBuild/CodePipeline events → OTel; GitHub Actions OTel receiver in ADOT
- ECR push per region in parallel to avoid bandwidth bottleneck

## Practice question

**Q.** Builds went from 7 to 14 minutes. Engineers want bigger runners. What do you do?

**Model answer.** Trace the workflow and find the critical path. Check per step whether it's CPU, I/O or network bound, and test with more cores before buying. Check P50 vs P90 for retry tax and look at artefact transfer and cache hit rates. Fix the dominant serial step first; Amdahl says parallelism won't save serial work.

## Exercise

Export the step timings of one CI run, draw the dependency graph and mark the critical path. Which step would you speed up first, and why not the slowest one?

## Takeaways

- CI is production on a deadline
- Optimise the critical path only
- Under 7 minutes keeps devs in flow

## Since the book (checked against documentation, 2026-11-27)

- OpenTelemetry now has CI/CD semantic conventions (first attributes in v1.27.0), so pipeline traces can use standard names.

## Official documentation

- [OpenTelemetry semantic conventions: CI/CD](https://opentelemetry.io/docs/specs/semconv/cicd/): Pipeline run and task spans
