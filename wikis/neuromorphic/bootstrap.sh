#!/usr/bin/env bash
# Bootstrap ~50 entries for the neuromorphic wiki.
#
# Stratifies by entity_type (the only axis where mixing kinds hurts the prompt).
# Each call is capped at 5 by the make_list template, so we issue multiple
# calls per type and feed the catalogue's existing titles back as --existing
# to steer the LLM away from repeats.
#
# Usage: bash wikis/neuromorphic/bootstrap.sh [--dry-run]

set -euo pipefail

WIKI=neuromorphic
WIKI_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$WIKI_DIR/../.." && pwd)"
DRY=""
if [[ "${1:-}" == "--dry-run" ]]; then DRY="--dry-run"; fi

cd "$REPO_ROOT"

# entity_type → "rounds:n" (each round is one LLM call asking for n entries)
declare -a PLAN=(
  "hardware:1:15"
  "organization:1:10"
  "algorithm:1:10"
  "person:1:10"
  "application:1:6"
  "concept:1:6"
)

existing_titles_for() {
  # Print one title per line for entries whose entity_type matches $1.
  local etype="$1"
  python3 - "$WIKI_DIR/catalogue" "$etype" <<'PY'
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
target = sys.argv[2]
if not root.is_dir():
    sys.exit(0)
for p in sorted(root.glob("*.json")):
    try:
        e = json.loads(p.read_text())
    except Exception:
        continue
    if (e.get("axes") or {}).get("entity_type") == target:
        t = e.get("title") or e.get("slug")
        if t:
            print(t)
PY
}

for spec in "${PLAN[@]}"; do
  IFS=':' read -r etype rounds n <<< "$spec"
  for i in $(seq 1 "$rounds"); do
    echo
    echo "=== entity_type=$etype  round $i/$rounds  n=$n ==="
    existing_args=()
    while IFS= read -r title; do
      [[ -n "$title" ]] && existing_args+=(--existing "$title")
    done < <(existing_titles_for "$etype")
    uv run tools/atlas.py generate \
      --wiki "$WIKI" \
      --n "$n" \
      --axis "entity_type=$etype" \
      $DRY \
      "${existing_args[@]}"
  done
done

echo
echo "=== final count ==="
ls "$WIKI_DIR/catalogue/" | wc -l
