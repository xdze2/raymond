#!/usr/bin/env bash
# Generate a list file for one axis combination using the Claude CLI.
# Usage: ./gen_list.sh <wiki> <gen_axis_1_value> <gen_axis_2_value> ... [freeform_value ...]
# Example: ./gen_list.sh data_atlas sensor buried individual medical

set -euo pipefail

WIKI="${1:-}"
if [[ -z "$WIKI" ]]; then
  echo "Usage: $0 <wiki> <gen_axis_values...> [freeform_values...]" >&2
  exit 1
fi
shift

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIKI_DIR="$SCRIPT_DIR/wikis/$WIKI"
WIKI_CONFIG="$WIKI_DIR/wiki.json"

if [[ ! -f "$WIKI_CONFIG" ]]; then
  echo "Error: $WIKI_CONFIG not found" >&2
  exit 1
fi

PROMPT_TEMPLATE="$WIKI_DIR/prompts/make_list.txt"
OUTPUT_DIR="$WIKI_DIR/catalogue"

if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "Error: prompt template not found at $PROMPT_TEMPLATE" >&2
  exit 1
fi

# Read axis ids from wiki.json
mapfile -t GEN_AXES < <(jq -r '.gen_axes[]' "$WIKI_CONFIG")
mapfile -t FREE_AXES < <(jq -r '.freeform_axes[]? // empty' "$WIKI_CONFIG")

REQUIRED=${#GEN_AXES[@]}
TOTAL_SLOTS=$((REQUIRED + ${#FREE_AXES[@]}))

if (( $# < REQUIRED )); then
  echo "Usage: $0 $WIKI ${GEN_AXES[*]} [${FREE_AXES[*]}]" >&2
  echo "Got $# values, need at least $REQUIRED for gen_axes." >&2
  exit 1
fi

# Build the placeholder substitutions and filename parts
FILENAME_PARTS=()
SED_ARGS=()
i=0
for axis in "${GEN_AXES[@]}"; do
  val="${1:-}"
  shift
  if [[ -z "$val" ]]; then
    echo "Error: missing value for axis '$axis'" >&2
    exit 1
  fi
  SED_ARGS+=(-e "s/{$axis}/$val/g")
  FILENAME_PARTS+=("$val")
  i=$((i + 1))
done

for axis in "${FREE_AXES[@]}"; do
  val="${1:-any}"
  [[ $# -gt 0 ]] && shift
  SED_ARGS+=(-e "s/{$axis}/$val/g")
  FILENAME_PARTS+=("$val")
done

mkdir -p "$OUTPUT_DIR"

# Join filename parts with underscore
JOINED=$(IFS=_; echo "${FILENAME_PARTS[*]}")
OUTPUT_FILE="$OUTPUT_DIR/list_${JOINED}.jsonl"

PROMPT=$(sed "${SED_ARGS[@]}" "$PROMPT_TEMPLATE")

echo "Wiki:       $WIKI"
echo "Axes:       ${GEN_AXES[*]} ${FREE_AXES[*]}"
echo "Values:     ${FILENAME_PARTS[*]}"
echo "Output:     $OUTPUT_FILE"

claude --print \
  --model claude-sonnet-4-6 \
  "$PROMPT" > "$OUTPUT_FILE"

echo "Done. Lines written: $(wc -l < "$OUTPUT_FILE")"
