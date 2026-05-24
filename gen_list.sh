#!/usr/bin/env bash
# Generate a list file for one axis combination using the Claude CLI.
# Usage: ./gen_list.sh <origin> <status> <scale> <domain>
# Example: ./gen_list.sh sensor buried individual medical

set -euo pipefail

ORIGIN="${1:-}"
STATUS="${2:-}"
SCALE="${3:-}"
DOMAIN="${4:-any}"

if [[ -z "$ORIGIN" || -z "$STATUS" || -z "$SCALE" ]]; then
  echo "Usage: $0 <origin> <status> <scale> [domain]"
  echo "  origin:  sensor | exhaust | declared | derived"
  echo "  status:  active | buried | missing | emerging | eroding"
  echo "  scale:   individual | organizational | systemic | planetary"
  echo "  domain:  medical | finance | agriculture | law-enforcement | ... (default: any)"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_TEMPLATE="$SCRIPT_DIR/prompts/make_list.txt"
OUTPUT_DIR="$SCRIPT_DIR/data/catalogue"
OUTPUT_FILE="$OUTPUT_DIR/list_${ORIGIN}_${STATUS}_${SCALE}_${DOMAIN}.jsonl"

if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "Error: prompt template not found at $PROMPT_TEMPLATE" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Substitute placeholders in the prompt template
PROMPT=$(sed \
  -e "s/{origin}/$ORIGIN/g" \
  -e "s/{status}/$STATUS/g" \
  -e "s/{scale}/$SCALE/g" \
  -e "s/{domain}/$DOMAIN/g" \
  "$PROMPT_TEMPLATE")

echo "Generating: origin=$ORIGIN  status=$STATUS  scale=$SCALE  domain=$DOMAIN"
echo "Output:     $OUTPUT_FILE"

claude --print \
  --model claude-sonnet-4-6 \
  "$PROMPT" > "$OUTPUT_FILE"

echo "Done. Lines written: $(wc -l < "$OUTPUT_FILE")"
