#!/usr/bin/env bash
# Rebuild wikis/<wiki>/catalogue/index.json from all .jsonl files present.
# Usage: ./update_index.sh <wiki>

set -euo pipefail

WIKI="${1:-}"
if [[ -z "$WIKI" ]]; then
  echo "Usage: $0 <wiki>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/wikis/$WIKI/catalogue"
INDEX_FILE="$OUTPUT_DIR/index.json"

if [[ ! -d "$OUTPUT_DIR" ]]; then
  echo "Error: $OUTPUT_DIR does not exist" >&2
  exit 1
fi

files=()
for f in "$OUTPUT_DIR"/*.jsonl; do
  [[ -e "$f" ]] || continue
  files+=("\"$(basename "$f")\"")
done

printf '[%s]\n' "$(IFS=', '; echo "${files[*]}")" > "$INDEX_FILE"

echo "Updated $INDEX_FILE with ${#files[@]} file(s):"
for f in "${files[@]}"; do echo "  $f"; done
