#!/usr/bin/env bash
# `lefthook install` requires a git repository. This repo is also a Copier
# template (CLAUDE.local.md); its documented instantiation flow does not run
# `git init`, so a fresh `copier copy` + `npm install` would otherwise hard-fail
# on first install with no useful error. Swallow ONLY that specific failure;
# let any other `lefthook install` error (corrupt config, permissions, etc.)
# surface and fail `npm install` normally.
set -uo pipefail

output=$(npx lefthook install 2>&1)
status=$?

if [ "$status" -ne 0 ]; then
  if echo "$output" | grep -q "not a git repository"; then
    echo "$output"
    echo "No git repository here (likely a fresh Copier instantiation) -- skipping hook install."
    exit 0
  fi
  echo "$output" >&2
  exit "$status"
fi

echo "$output"
