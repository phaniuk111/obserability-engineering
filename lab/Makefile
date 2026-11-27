# Observability Engineering lab. `make help` lists targets.
CH = docker compose exec -T clickhouse clickhouse-client --user otel --password otel --multiquery --format PrettyCompactNoEscapes

help:            ## Show targets
	@grep -E '^[a-z-]+:.*##' Makefile | sed 's/:.*## /\t/'

up:              ## Build and start everything (app, Collector, ClickHouse, Prometheus, Jaeger, Grafana)
	docker compose up -d --build
	@$(MAKE) --no-print-directory urls

down:            ## Stop and delete data
	docker compose down -v

urls:            ## Where to look
	@echo "Jaeger      http://localhost:16686   (sampled traces)"
	@echo "Grafana     http://localhost:3000    (dashboard: Checkout)"
	@echo "Prometheus  http://localhost:9090/alerts"
	@echo "Collector   http://localhost:8889/metrics"
	@echo "Queries     make q F=03_bubbleup"

fault-on:        ## Break discount validation for the new code format
	curl -fsS -X POST localhost:8082/admin/fault -H 'content-type: application/json' -d '{"on":true}'; echo

fault-off:       ## Fix it
	curl -fsS -X POST localhost:8082/admin/fault -H 'content-type: application/json' -d '{"on":false}'; echo

q:               ## Run a lab query file, e.g. make q F=03_bubbleup
	@$(CH) < clickhouse/queries/$(F).sql

sql:             ## Interactive ClickHouse shell
	docker compose exec clickhouse clickhouse-client --user otel --password otel --database otel

smoke:           ## Start the stack and check every lab's claim against it
	./smoke-test.sh

test:            ## No Docker: real SDK + OTLP + embedded ClickHouse, all lab queries (about a minute)
	cd tests && python3 -m unittest -v

nodocker:        ## No Docker: same as test, but prints every query result
	cd tests && python3 harness.py

lint:            ## Structural lint of the Collector configs
	python3 collector/check_config.py

.PHONY: help up down urls fault-on fault-off q sql smoke test nodocker lint
