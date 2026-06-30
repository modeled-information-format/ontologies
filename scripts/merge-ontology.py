#!/usr/bin/env python3
"""Reconcile a domain ontology that diverged at the same version across the
harness and the canonical registry, into one merged, schema-valid pack.

Background: research-harness-template authored Round-4 expansions to several
domain packs IN PLACE at version 0.1.0, so the harness copy and the registry
copy carry different content under the *same* version — an ADR-0010 violation.

The harness copy is the newer Round-4 design. This tool computes the name-level
delta between the two (entity_types, relationships, traits), and — when the
harness is a superset (no registry-only names) — adopts the harness content
verbatim, bumps the version, and validates the result against the canonical MIF
ontology schema. If the registry carries names the harness lacks, the tool
refuses and lists them: that is a genuine divergence a human must reconcile, not
a mechanical superset.

Usage:
    merge-ontology.py <id> --harness <yaml> --registry <yaml> \
        --schema <ontology.schema.json> --out <yaml> --version X.Y.Z
    merge-ontology.py <id> ... --check     # validate + report only; write nothing
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
import jsonschema


def load(p: Path) -> dict:
    return yaml.safe_load(p.read_text())


def names(field) -> set:
    """Names in a field that may be a list of {name,...} or a dict keyed by name."""
    if isinstance(field, dict):
        return set(field.keys())
    if isinstance(field, list):
        return {i["name"] for i in field if isinstance(i, dict) and "name" in i}
    return set()


def delta(h: dict, r: dict, key: str, report: list) -> set:
    """Report harness-added and registry-only names for one field; return registry-only."""
    hn, rn = names(h.get(key)), names(r.get(key))
    for n in sorted(hn - rn):
        report.append(f"  {key}: '{n}' added in harness (Round-4)")
    reg_only = rn - hn
    for n in sorted(reg_only):
        report.append(f"  {key}: '{n}' REGISTRY-ONLY — harness lacks it (needs human reconciliation)")
    return reg_only


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--harness", required=True, type=Path)
    ap.add_argument("--registry", required=True, type=Path)
    ap.add_argument("--schema", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--version", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    h, r = load(a.harness), load(a.registry)
    report: list[str] = []
    reg_only: set = set()
    for key in ("entity_types", "relationships", "traits"):
        reg_only |= delta(h, r, key, report)

    if reg_only:
        print(f"merge-ontology[{a.id}]: REFUSING — registry has names the harness lacks "
              f"(not a clean superset): {sorted(reg_only)}", file=sys.stderr)
        print("\n".join(report), file=sys.stderr)
        return 1

    # Harness is a superset of the registry: adopt it verbatim, bump the version.
    merged = dict(h)
    merged.setdefault("ontology", {})
    merged["ontology"] = {**h.get("ontology", {}), "version": a.version}

    schema = json.loads(a.schema.read_text())
    try:
        jsonschema.validate(merged, schema)
    except jsonschema.ValidationError as e:
        loc = "/".join(map(str, e.absolute_path)) or "root"
        print(f"merge-ontology[{a.id}]: result FAILS schema at {loc}: {e.message}", file=sys.stderr)
        return 1

    n_e, n_r = len(names(merged.get("entity_types"))), len(names(merged.get("relationships")))
    print(f"merge-ontology[{a.id}]: harness-superset adopted -> v{a.version}, "
          f"{n_e} entity_types, {n_r} relationships, schema-valid")
    if report:
        print("\n".join(report))
    if a.check:
        return 0
    if not a.out:
        print("merge-ontology: --out required when not --check", file=sys.stderr)
        return 2
    a.out.write_text("---\n" + yaml.safe_dump(merged, sort_keys=False, allow_unicode=True, width=100))
    print(f"merge-ontology[{a.id}]: wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
