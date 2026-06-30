#!/usr/bin/env bash
# gen-ontology-index.sh — produce ontologies/index.json, the machine-readable
# registry the research harness fetches ontologies against ON DEMAND.
#
# For each ontologies/<id>.ontology.yaml it records:
#   <id> -> { version, file, sha256, extends[] }
# so a consumer can, given an ontology id: locate the file, pin+verify its
# sha256, and resolve its `extends` closure (to fetch ancestor layers too).
#
# Output is byte-stable (jq -S, sorted keys) so a re-run is a no-op when nothing
# changed — the property the drift gate relies on.
#
# Usage: scripts/gen-ontology-index.sh [--check]
#   --check  Regenerate into a temp file and diff against the committed index;
#            exit non-zero if they differ (CI drift gate). Writes nothing.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 2

ONT_DIR="ontologies"
OUT="$ONT_DIR/index.json"
CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

command -v yq >/dev/null || { echo "gen-ontology-index: yq is required" >&2; exit 2; }
command -v jq >/dev/null || { echo "gen-ontology-index: jq is required" >&2; exit 2; }
if command -v sha256sum >/dev/null; then
  SHA="sha256sum"
elif command -v shasum >/dev/null; then
  SHA="shasum -a 256"
else
  echo "gen-ontology-index: sha256sum or shasum is required" >&2; exit 2
fi

acc=$(mktemp); echo '{}' > "$acc"
trap 'rm -f "$acc" "$acc.2"' EXIT

for f in "$ONT_DIR"/*.ontology.yaml; do
  [ -e "$f" ] || continue
  id=$(yq -r '.ontology.id // ""' "$f")
  if [ -z "$id" ]; then
    echo "gen-ontology-index: skip $f (no .ontology.id)" >&2
    continue
  fi
  # duplicate id would silently last-write-wins in the accumulator — fail loudly.
  if jq -e --arg id "$id" 'has($id)' "$acc" >/dev/null 2>&1; then
    echo "gen-ontology-index: duplicate ontology id '$id' (second occurrence: $f)" >&2
    exit 1
  fi
  version=$(yq -r '.ontology.version // "0.0.0"' "$f")
  # normalize extends to an array: missing -> [], a scalar -> [scalar], a sequence -> as-is.
  extends=$(yq -o=json -I=0 '[.ontology.extends // []] | flatten' "$f")
  sha=$($SHA "$f" | awk '{print $1}')
  file=$(basename "$f")
  jq --arg id "$id" --arg v "$version" --arg file "$file" --arg sha "$sha" --argjson ext "$extends" \
     '.[$id] = {version:$v, file:$file, sha256:$sha, extends:$ext}' "$acc" > "$acc.2"
  mv "$acc.2" "$acc"
done

rendered=$(jq -S --arg src "https://mif-spec.dev/ontologies/" \
  '{schema:"mif-ontology-index/v1", source:$src, ontologies:.}' "$acc")

if [ "$CHECK" = 1 ]; then
  if ! diff -u <(cat "$OUT" 2>/dev/null) <(printf '%s\n' "$rendered") >/dev/null 2>&1; then
    echo "gen-ontology-index: --check FAILED — $OUT is stale; run scripts/gen-ontology-index.sh" >&2
    diff -u <(cat "$OUT" 2>/dev/null) <(printf '%s\n' "$rendered") >&2 || true
    exit 1
  fi
  echo "gen-ontology-index: --check OK ($OUT matches a fresh regeneration)"
  exit 0
fi

printf '%s\n' "$rendered" > "$OUT"
echo "gen-ontology-index: wrote $OUT ($(jq '.ontologies|length' "$OUT") ontologies)"
