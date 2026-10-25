#!/usr/bin/env bash
# Local quality gate for the domain/tooling repo — run BEFORE any deploy.
# Must be green with zero Home Assistant access (policy is pure Python).
#
#   tools/qa.sh            run everything
#   tools/qa.sh fast       skip the summarize.py consistency check
#
# Exit 1 on any failure. Managed code = domain/ + tests/ (ruff scope);
# tools/summarize.py is a legacy live script and deliberately not linted.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

echo "== ruff (domain, tests) =="
uv run ruff check domain tests || exit 1

echo "== mypy (domain) =="
uv run mypy domain || exit 1

echo "== pytest =="
uv run pytest || exit 1

if [[ "${1:-}" == "fast" ]]; then
  echo "(fast: skipping summarize.py consistency check)"
else
  echo "== summarize.py consistency (docs never drift) =="
  uv run python3 tools/summarize.py >/dev/null || {
    echo "summarize.py consistency check FAILED (unknown input_* refs)." >&2
    exit 1
  }
fi

echo "QA OK."