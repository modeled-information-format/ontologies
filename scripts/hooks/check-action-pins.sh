#!/usr/bin/env bash
# Local replica of the org's central pin-check.yml gate (see .github/workflows/ci.yml):
# every `uses:` in a workflow file must be pinned to a full 40-char commit SHA, not a
# tag or branch ref. Catches the same failure ci.yml's pin-check job would, before push.
#
# This is an independent copy of that gate's logic, not a shared implementation --
# it can silently drift if the central modeled-information-format/.github pin-check.yml
# changes its exemption rules (e.g. digest-pinned `docker://...@sha256:` refs, or new
# local-action patterns). If pin-check.yml's logic changes, check whether this script
# needs the same update.
#
# Usage: check-action-pins.sh <file> [file...]
set -euo pipefail

files=("$@")
[ "${#files[@]}" -eq 0 ] && exit 0

fail=0
for f in "${files[@]}"; do
  [ -f "$f" ] || continue
  total=$(wc -l < "$f")
  # Match every `uses:` line, not just ones with the ref inline — reusable-workflow
  # calls in this repo use the YAML folded-scalar form (`uses: >-` with the actual
  # `owner/repo@ref` on the next line), which a same-line-only pattern would miss.
  while IFS= read -r match; do
    [ -z "$match" ] && continue
    lineno="${match%%:*}"
    rest="${match#*:}"
    body="${rest%%#*}"   # drop trailing inline comment before parsing
    if [[ "$body" =~ ^[[:space:]]*(-[[:space:]]*)?uses:[[:space:]]*(\>-|\|-)[[:space:]]*$ ]]; then
      nextline=$((lineno + 1))
      [ "$nextline" -gt "$total" ] && continue
      body=$(sed -n "${nextline}p" "$f")
      rest="$body"
      lineno=$nextline
    fi
    [[ "$body" == *"@"* ]] || continue
    ref=$(awk -F'@' '{print $NF}' <<<"$body" | awk '{print $1}' | tr -d '"'"'"'')
    if [[ ! "$ref" =~ ^[0-9a-f]{40}$ ]]; then
      echo "$f:$lineno: 'uses:' ref is not a full 40-char commit SHA: $rest"
      fail=1
    fi
  done < <(grep -nE '^[[:space:]]*(-[[:space:]]*)?uses:' "$f" || true)
done

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "ERROR: one or more workflow 'uses:' refs are not pinned to a full commit SHA."
  echo "Resolve the tag to its commit SHA (e.g. 'gh api repos/<owner>/<repo>/git/ref/tags/<tag>')"
  echo "and pin to that instead. This mirrors ci.yml's pin-check gate."
  exit 1
fi
