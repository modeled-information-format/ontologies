#!/usr/bin/env python3
"""Validate ontology YAML files: schema conformance via ajv (the repo's JSON Schema
tool, matching MIF's own JSON-LD validation job), plus entity-type subsumption
integrity (cross-ontology `subtype_of` resolution, acyclicity, substitutability) —
graph checks no JSON Schema validator can express.

Ported from MIF's retired scripts/validate-ontologies.py (removed by ADR-019 when
ontology content moved to this repo without the validation following it — see
issue #51). Adapted to this repo's actual layout: only ontologies/*.ontology.yaml
exists here, there is no ontologies/examples/ directory.

The schema itself is not vendored in this repo. ontology.schema.json's $id
(https://mif-spec.dev/schema/ontology/ontology.schema.json) is deliberately
resolvable, unversioned, and stable (ADR-007) — CI fetches it fresh from that
canonical URL rather than carrying a local copy that could drift from the
source of record in MIF. See ci.yml's "Validate ontology files" step.
"""

import json
import os
import subprocess
import sys
import tempfile
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from typing import Any

import yaml


def load_yaml(yaml_path: Path) -> Any:
    """Load YAML file."""
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def _ajv_validate(data: dict, schema_path: Path) -> list[str]:
    """Validate `data` against `schema_path` (draft2020, formats) via
    scripts/ajv-validate.mjs -- a thin wrapper around the ajv/ajv-formats
    libraries, deliberately not the `ajv-cli` package (see that script's
    docstring for why). Fail-closed: a missing Node/script is reported as an
    error, never a silent pass."""
    repo_root = Path(__file__).parent.parent
    validator = repo_root / "scripts" / "ajv-validate.mjs"
    fd, tmp = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f)
        proc = subprocess.run(
            ["node", str(validator), "--schema", str(schema_path), "--data", tmp],
            capture_output=True, text=True,
        )
        if proc.returncode == 0:
            return []
        out = (proc.stderr or proc.stdout or "").strip()
        return [f"  - schema: {ln}" for ln in out.splitlines() if ln.strip()][:20]
    except FileNotFoundError:
        return ["  - schema: node not found on PATH"]
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _entity_types(ontology: Any) -> list[dict]:
    """Normalize entity_types (list, or name-keyed dict) to a list of dicts. Tolerant of
    schema-invalid input (non-dict ontology, scalar entity_types) — never raises."""
    if not isinstance(ontology, dict):
        return []
    ets = ontology.get("entity_types")
    if isinstance(ets, dict):
        # The key is the authoritative name — spread first so a stray `name` in the value can't override it.
        return [{**(v if isinstance(v, dict) else {}), "name": k} for k, v in ets.items()]
    if isinstance(ets, list):
        return [et for et in ets if isinstance(et, dict)]
    return []


def _type_info(ontology: dict) -> dict[str, dict]:
    """Map entity-type name -> {'required': set, 'subtype_of': list} for one ontology."""
    info: dict[str, dict] = {}
    for et in _entity_types(ontology):
        name = et.get("name")
        if not isinstance(name, str) or not name:
            continue
        sch = et.get("schema")
        req = (sch.get("required") if isinstance(sch, dict) else None) or []
        req = req if isinstance(req, list) else []
        sub = et.get("subtype_of") or []
        sub = sub if isinstance(sub, list) else [sub]
        info[name] = {
            # string-only: hashable + fail-closed on malformed YAML (ajv reports the bad type).
            "required": {r for r in req if isinstance(r, str)},
            # Only string parents: keeps `visible.get(p)` / `p in graph` hashable and
            # fail-closed when the YAML is malformed (the schema flags the bad type separately).
            "subtype_of": [s for s in sub if isinstance(s, str)],
        }
    return info


def load_ontology_corpus(repo_root: Path) -> dict[str, dict]:
    """Load every ontology YAML keyed by its id: {id: {'extends': [...], 'types': {name: info}}}."""
    corpus: dict[str, dict] = {}
    ontology_dir = repo_root / "ontologies"
    if not ontology_dir.exists():
        return corpus
    for f in ontology_dir.glob("*.ontology.yaml"):
        try:
            data = load_yaml(f)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        ob = data.get("ontology")
        if not isinstance(ob, dict):
            continue
        oid = ob.get("id")
        if not isinstance(oid, str) or not oid:
            continue
        ext = ob.get("extends") or []
        ext = ext if isinstance(ext, list) else [ext]
        corpus[oid] = {
            "extends": [e for e in ext if isinstance(e, str)],
            "types": _type_info(data),
        }
    return corpus


def visible_types(oid: str, corpus: dict[str, dict], _seen: set | None = None) -> dict[str, dict]:
    """Type infos visible to ontology `oid`: its own ∪ those of every ontology it
    transitively `extends`. Own definitions win on a name collision."""
    _seen = _seen if _seen is not None else set()
    if oid in _seen or oid not in corpus:
        return {}
    _seen.add(oid)
    merged: dict[str, dict] = {}
    for parent in corpus[oid]["extends"]:
        merged.update(visible_types(parent, corpus, _seen))
    merged.update(corpus[oid]["types"])
    return merged


def _subtype_cycles(graph: dict[str, dict]) -> list[str]:
    """Cycle detection over the subtype_of graph via graphlib.TopologicalSorter, which
    reports the ACTUAL cycle nodes (not every type that merely depends on a cycle) and is
    iterative (no recursion limit). Self-edges are handled by the caller."""
    ts: TopologicalSorter = TopologicalSorter()
    for n, info in graph.items():
        preds = [p for p in info.get("subtype_of", []) if p in graph and p != n]
        ts.add(n, *preds)
    try:
        ts.prepare()
    except CycleError as e:
        cycle = e.args[1] if len(e.args) > 1 else []
        return [f"  - subtype_of cycle: {' -> '.join(str(c) for c in cycle)}"]
    return []


def check_subtype_of(ontology: dict, visible: dict[str, dict]) -> list[str]:
    """Entity-type subsumption integrity for one ontology, resolved against `visible`
    (its own types ∪ those of every ontology it extends): every `subtype_of` parent must
    resolve to a visible type, no type may be its own subtype, a subtype's `required` set
    must include each parent's (substitutability), and the graph must be acyclic.
    """
    errors: list[str] = []
    local = _type_info(ontology)
    for name, info in local.items():
        for p in info["subtype_of"]:
            if p == name:
                errors.append(f"  - entity_type '{name}': subtype_of cannot reference itself")
                continue
            parent = visible.get(p)
            if parent is None:
                errors.append(
                    f"  - entity_type '{name}': subtype_of parent '{p}' is not a declared "
                    f"entity type in this ontology or any it extends"
                )
                continue
            missing = parent["required"] - info["required"]
            if missing:
                errors.append(
                    f"  - entity_type '{name}': subtype_of '{p}' but its required set is missing "
                    f"parent field(s) {sorted(missing)} (a subtype must require at least the parent's)"
                )
    # Cycle detection over LOCAL types only: a cycle is attributed to the ontology that
    # declares it, not re-reported by every descendant. (extends is one-way, so a cycle
    # cannot span the ancestor boundary; an ancestor-internal cycle fails when the
    # ancestor is itself validated.)
    errors.extend(_subtype_cycles(local))
    return errors


def validate_ontology(ontology_path: Path, schema_path: Path, corpus: dict[str, dict]) -> list[str]:
    """Validate a single ontology file against the schema (ajv) and subsumption integrity."""
    errors = []
    try:
        ontology = load_yaml(ontology_path)
        errors.extend(_ajv_validate(ontology, schema_path))
        ob = ontology.get("ontology") if isinstance(ontology, dict) else None
        oid = ob.get("id") if isinstance(ob, dict) else None
        visible = visible_types(oid, corpus) if isinstance(oid, str) and oid else {}
        if not visible:
            # oid missing from the preloaded corpus (e.g. an id collision left this
            # file's entry overwritten) -- fall back to this file's own local types
            # rather than treating every locally-declared parent as unresolvable.
            visible = _type_info(ontology)
        errors.extend(check_subtype_of(ontology, visible))
    except yaml.YAMLError as e:
        errors.append(f"  - YAML parse error: {e}")
    except Exception as e:
        errors.append(f"  - Unexpected error: {e}")
    return errors


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    schema_env = os.environ.get("ONTOLOGY_SCHEMA_PATH")
    schema_path = Path(schema_env) if schema_env else repo_root / "schema" / "ontology.schema.json"
    ontology_dir = repo_root / "ontologies"

    if not schema_path.exists():
        print(f"ERROR: Schema not found: {schema_path}")
        print("Set ONTOLOGY_SCHEMA_PATH, or fetch it first "
              "(see ci.yml's 'Validate ontology files' step).")
        sys.exit(1)

    corpus = load_ontology_corpus(repo_root)
    all_errors = {}

    if ontology_dir.exists():
        for ontology_file in sorted(ontology_dir.glob("*.ontology.yaml")):
            errors = validate_ontology(ontology_file, schema_path, corpus)
            if errors:
                rel_path = ontology_file.relative_to(repo_root)
                all_errors[str(rel_path)] = errors

    if all_errors:
        print("Ontology validation FAILED:")
        for file_path, errors in all_errors.items():
            print(f"\n{file_path}:")
            for error in errors:
                print(error)
        sys.exit(1)
    else:
        print("All ontology files validated successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
