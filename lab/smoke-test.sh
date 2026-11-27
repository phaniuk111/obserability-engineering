#!/usr/bin/env bash
# Starts the stack, waits for traffic, turns the fault on, and checks what each lab claims.
# I (the author) could not run Docker where this was written, so this script is the proof.
# If a check fails, the hint under it says where to look.
set -uo pipefail
cd "$(dirname "$0")"
fails=0
ch() { docker compose exec -T clickhouse clickhouse-client --user otel --password otel -q "$1" 2>/dev/null; }
check() { # check "name" "actual" "test-expression using \$v" "hint"
  local name=$1 v=$2 expr=$3 hint=$4
  if eval "$expr" >/dev/null 2>&1; then printf 'PASS  %s (%s)\n' "$name" "$v"; else printf 'FAIL  %s (got: %s)\n      hint: %s\n' "$name" "$v" "$hint"; fails=$((fails+1)); fi
}
wait_for() { # wait_for "description" seconds command...
  local what=$1 secs=$2; shift 2
  for _ in $(seq "$secs"); do "$@" >/dev/null 2>&1 && return 0; sleep 1; done
  echo "FAIL  timed out waiting for $what"; fails=$((fails+1)); return 1
}

echo "== starting"
docker compose up -d --build || { echo "docker compose failed"; exit 1; }
wait_for "storefront" 120 curl -fsS localhost:8080/healthz
wait_for "collector health" 120 curl -fsS localhost:13133
wait_for "spans in ClickHouse" 120 bash -c 'n=$(docker compose exec -T clickhouse clickhouse-client --user otel --password otel -q "SELECT count() FROM otel.otel_traces" 2>/dev/null); [ "${n:-0}" -gt 200 ]'

echo "== healthy traffic"
v=$(ch "SELECT uniqExact(ServiceName) FROM otel.otel_traces")
check "three services report spans" "$v" '[ "$v" = 3 ]' "docker compose logs otel-collector | tail -50"
v=$(ch "SELECT count() FROM otel.otel_traces WHERE SpanAttributes['http.route'] = '/checkout' AND SpanAttributes['app.user.id'] != ''")
check "checkout spans carry the wide-event attributes" "$v" '[ "${v:-0}" -gt 50 ]' "check app/shop.py attributes and OTEL_SEMCONV_STABILITY_OPT_IN"
v=$(ch "SELECT countIf(position(SpanAttributes['user.email'], '@') > 0) FROM otel.otel_traces")
check "no plaintext email stored (Collector hashed it)" "$v" '[ "$v" = 0 ]' "attributes/pii must be in the traces/in pipeline of collector/local.yaml"
v=$(curl -fsS localhost:8889/metrics | grep -c '^shop_calls_total')
check "span metrics exposed as shop_calls_total" "$v" '[ "${v:-0}" -gt 0 ]' "curl localhost:8889/metrics | grep calls ; then fix the names in prometheus/rules.yml and grafana/dashboards"
wait_for "Prometheus scrape" 60 bash -c 'curl -fsS "localhost:9090/api/v1/query?query=shop_calls_total" | grep -q service_name'
v=$(curl -fsS "localhost:9090/api/v1/rules" | grep -c CheckoutErrorBudgetFastBurn)
check "Prometheus loaded the SLO rules" "$v" '[ "${v:-0}" -gt 0 ]' "docker compose logs prometheus"
sleep 15   # let tail sampling decide (decision_wait 5s) and flush
v=$(ch "SELECT round((SELECT uniqExact(TraceId) FROM otel.otel_traces_sampled) / (SELECT uniqExact(TraceId) FROM otel.otel_traces) * 100)")
check "tail sampling kept roughly 10% of healthy traces" "$v" '[ "${v:-0}" -ge 3 ] && [ "$v" -le 30 ]' "tail_sampling policies in collector/local.yaml"
v=$(curl -fsS localhost:16686/api/services | grep -c storefront)
check "Jaeger has the sampled traces" "$v" '[ "${v:-0}" -gt 0 ]' "docker compose logs jaeger otel-collector"

echo "== fault on (waiting 60s for traffic)"
make --no-print-directory fault-on >/dev/null
sleep 60
v=$(docker compose exec -T clickhouse clickhouse-client --user otel --password otel --multiquery --format TSV < clickhouse/queries/03_bubbleup.sql 2>/dev/null | head -1 | cut -f1,2 | tr '\t' '=')
check "BubbleUp query names the culprit" "$v" '[ "$v" = "app.discount.format=v2" ]' "make q F=03_bubbleup"
v=$(ch "SELECT (SELECT uniqExact(TraceId) FROM otel.otel_traces WHERE StatusCode IN ('Error','STATUS_CODE_ERROR')) - (SELECT uniqExact(TraceId) FROM otel.otel_traces_sampled WHERE StatusCode IN ('Error','STATUS_CODE_ERROR'))")
check "every error trace survived sampling (0-2 may still be in flight)" "$v" '[ "${v:-99}" -le 2 ]' "make q F=05_sampling"
v=$(curl -fsS "localhost:9090/api/v1/query?query=slo:checkout_slow_ratio:rate1m" | grep -o '"value":\[[^]]*\]' | grep -o '"[0-9.e-]*"' | tr -d '"')
check "latency SLI sees the fault (slow ratio over 2%)" "$v" 'awk "BEGIN{exit !(${v:-0} > 0.02)}"' "bucket le=0.5 must exist: curl localhost:8889/metrics | grep shop_duration_seconds_bucket"
make --no-print-directory fault-off >/dev/null

echo
if [ "$fails" = 0 ]; then echo "ALL CHECKS PASSED. Open the labs in labs/ (make urls)."; else echo "$fails check(s) failed. The stack is still running: make urls"; fi
exit "$fails"
