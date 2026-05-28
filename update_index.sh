#!/usr/bin/env bash
# Rebuild data/catalogue/index.json from all .jsonl files present in the directory.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/data/catalogue"
INDEX_FILE="$OUTPUT_DIR/index.json"

files=()
for f in "$OUTPUT_DIR"/*.jsonl; do
  [[ -e "$f" ]] || continue
  files+=("\"$(basename "$f")\"")
done

printf '[%s]\n' "$(IFS=', '; echo "${files[*]}")" > "$INDEX_FILE"

echo "Updated $INDEX_FILE with ${#files[@]} file(s):"
for f in "${files[@]}"; do echo "  $f"; done
