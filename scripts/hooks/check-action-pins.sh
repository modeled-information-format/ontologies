#!/usr/bin/env bash
# Local replica of the org's central pin-check.yml gate (see .github/workflows/ci.yml):
# every `uses:` in a workflow file must be pinned to a full 40-char commit SHA, not a
# tag or branch ref. Catches the same failure ci.yml's pin-check job would, before push.
#
# Usage: check-action-pins.sh <file> [file...]
set -euo pipefail

files=("$@")
[ "${#files[@]}" -eq 0 ] && exit 0

fail=0
for f in "${files[@]}"; do
  [ -f "$f" ] || continue
  while IFS= read -r match; do
    [ -z "$match" ] && continue
    lineno="${match%%:*}"
    rest="${match#*:}"
    ref=$(awk -F'@' '{print $NF}' <<<"$rest" | awk '{print $1}' | tr -d '"'"'"'')
    if [[ ! "$ref" =~ ^[0-9a-f]{40}$ ]]; then
      echo "$f:$lineno: 'uses:' ref is not a full 40-char commit SHA: $rest"
      fail=1
    fi
  done < <(grep -nE '^\s*(-\s*)?uses:\s*\S+@\S+' "$f" || true)
done

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "ERROR: one or more workflow 'uses:' refs are not pinned to a full commit SHA."
  echo "Resolve the tag to its commit SHA (e.g. 'gh api repos/<owner>/<repo>/git/refs/tags/<tag>')"
  echo "and pin to that instead. This mirrors ci.yml's pin-check gate."
  exit 1
fi
