#!/usr/bin/env bash
# Explore every catalogue entry with status=generated.
#
# For each slug, runs `atlas.py explore` which: fetches Wikipedia/Wikidata
# enrichment, does a DDG search, calls the LLM with make_page.txt, and
# flips status generated -> explored.
#
# Stops on the first failure. Re-running resumes automatically since the
# status filter skips already-explored entries.
#
# Usage:
#   bash wikis/neuromorphic/explore_all.sh              # all generated entries
#   bash wikis/neuromorphic/explore_all.sh --limit 3    # first 3 only
#   bash wikis/neuromorphic/explore_all.sh --sleep 5    # 5s between entries
#   bash wikis/neuromorphic/explore_all.sh --limit 3 --sleep 5

set -euo pipefail

WIKI=neuromorphic
WIKI_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$WIKI_DIR/../.." && pwd)"
LIMIT=0
SLEEP=2

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    --sleep) SLEEP="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

cd "$REPO_ROOT"

mapfile -t SLUGS < <(python3 - "$WIKI_DIR/catalogue" "$LIMIT" <<'PY'
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
limit = int(sys.argv[2])
out = []
for p in sorted(root.glob("*.json")):
    try:
        e = json.loads(p.read_text())
    except Exception:
        continue
    if e.get("status") == "generated":
        out.append(p.stem)
if limit > 0:
    out = out[:limit]
for s in out:
    print(s)
PY
)

total="${#SLUGS[@]}"
if [[ "$total" -eq 0 ]]; then
  echo "no entries with status=generated — nothing to do"
  exit 0
fi

echo "=== exploring $total entries (sleep=${SLEEP}s between) ==="
i=0
for slug in "${SLUGS[@]}"; do
  i=$((i + 1))
  echo
  echo "--- [$i/$total] $slug ---"
  uv run tools/atlas.py explore --wiki "$WIKI" --slug "$slug"
  if [[ "$i" -lt "$total" && "$SLEEP" -gt 0 ]]; then
    sleep "$SLEEP"
  fi
done

echo
echo "=== done: explored $total ==="
