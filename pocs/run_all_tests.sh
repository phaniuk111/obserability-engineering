#!/usr/bin/env bash
# Runs every POC's tests. Python 3.10+, standard library only.
set -euo pipefail
cd "$(dirname "$0")"
status=0
for d in [0-9][0-9]_*/; do
  printf '%-28s ' "${d%/}"
  if out=$(cd "$d" && python3 -m unittest -q 2>&1); then
    echo "$out" | grep -E '^Ran ' | tr '\n' ' '; echo "OK"
  else
    echo "FAILED"; echo "$out"; status=1
  fi
done
exit $status
