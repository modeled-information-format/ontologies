#!/usr/bin/env python3
"""Validate namespace consistency across the ontology corpus.

This is a fresh check, not a port. MIF's retired scripts/validate-namespaces.py
(removed alongside validate-ontologies.py by ADR-019) validated *memory files'*
frontmatter `namespace:` field against the namespaces declared by their
referenced ontology -- this repo holds only ontology *definitions*, none of
that script's memory-example directories exist here, and every code path in
its `validate_memory_namespace` returned an empty error list regardless of
outcome, so it was already close to a no-op. See issue #51 / #53 for the
full reasoning.

What this script actually checks, given each ontology declares a `namespaces:`
tree (root categories -> nested `children`, each with a `type_hint` of
semantic/episodic/procedural per ontology.schema.json) and an `extends` list
of ancestor ontologies:

1. Duplicate namespace keys within one ontology's own tree. YAML silently
   keeps the *last* occurrence of a duplicate mapping key, so a copy-paste
   mistake would otherwise vanish before schema validation ever saw it --
   ajv validates the parsed (already-collapsed) structure and cannot catch
   this. Detected here with a duplicate-key-raising loader.
2. Cross-ontology type_hint consistency: if a full namespace path (e.g.
   "semantic/science") is declared both by an ontology and by one of its
   `extends` ancestors, its `type_hint` must agree -- the same path
   resolving to a different memory-type category in ancestor vs. descendant
   is exactly the kind of silent ambiguity a memory consumer can't detect on
   its own. A path may deliberately be *reused* with matching type_hint (a
   descendant re-describing the same category); it may not mean something
   different depending on which ontology in the extends chain you're
   resolving against.
3. Dangling `replaces` references: `replaces` names the namespace path a
   given entry supersedes for migration purposes -- if that path isn't
   actually declared by any ontology in the `extends` closure, the
   "migration" points nowhere.
"""

import sys
from pathlib import Path
from typing import Any

import yaml


class DuplicateKeyError(Exception):
    pass


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that raises on duplicate mapping keys instead of silently
    keeping the last one -- yaml.safe_load's default behavior would hide
    exactly the class of bug this script exists to catch."""


def _construct_mapping(loader: yaml.SafeLoader, node: yaml.Node, deep: bool = False) -> dict:
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(f"duplicate key '{key}'")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def load_yaml_strict(yaml_path: Path) -> Any:
    with open(yaml_path) as f:
        return yaml.load(f, Loader=_UniqueKeyLoader)


def _flatten_namespaces(tree: Any, prefix: str = "") -> dict[str, dict]:
    """{namespaces: {...}} -> {full/path: {type_hint, description, replaces}}."""
    flat: dict[str, dict] = {}
    if not isinstance(tree, dict):
        return flat
    for name, entry in tree.items():
        if not isinstance(name, str) or not isinstance(entry, dict):
            continue
        path = f"{prefix}{name}" if not prefix else f"{prefix}/{name}"
        flat[path] = {
            "type_hint": entry.get("type_hint"),
            "description": entry.get("description"),
            "replaces": entry.get("replaces"),
        }
        children = entry.get("children")
        if isinstance(children, dict):
            flat.update(_flatten_namespaces(children, path))
    return flat


def load_corpus(repo_root: Path) -> dict[str, dict]:
    """{ontology_id: {'extends': [...], 'namespaces': {full_path: info}}}, plus a
    'file' key for error reporting. Files that fail to parse (including on a
    duplicate-key error) are silently skipped here -- check_duplicate_keys already
    reports duplicate-key failures separately, and a file that's absent from the
    corpus for any other parse reason surfaces as broken subtype_of/schema
    references from validate-ontologies.py, not from this script."""
    corpus: dict[str, dict] = {}
    ontology_dir = repo_root / "ontologies"
    if not ontology_dir.exists():
        return corpus
    for f in sorted(ontology_dir.glob("*.ontology.yaml")):
        try:
            data = load_yaml_strict(f)
        except (yaml.YAMLError, DuplicateKeyError):
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
            "file": f.name,
            "extends": [e for e in ext if isinstance(e, str)],
            "namespaces": _flatten_namespaces(data.get("namespaces") or {}),
        }
    return corpus


def ancestor_namespaces(oid: str, corpus: dict[str, dict], _seen: set | None = None) -> dict[str, dict]:
    """Full-path namespace map visible from oid's `extends` ancestors (NOT including
    oid's own tree) -- own definitions of the nearer ancestor win on a name collision
    among ancestors themselves, mirroring validate-ontologies.py's visible_types."""
    _seen = _seen if _seen is not None else set()
    if oid in _seen or oid not in corpus:
        return {}
    _seen.add(oid)
    merged: dict[str, dict] = {}
    for parent in corpus[oid]["extends"]:
        if parent not in corpus:
            continue
        merged.update(ancestor_namespaces(parent, corpus, _seen))
        merged.update(corpus[parent]["namespaces"])
    return merged


def check_duplicate_keys(repo_root: Path) -> dict[str, list[str]]:
    """Re-parse every ontology file strictly, reporting any that fail on a
    duplicate namespace key (or any other duplicate mapping key)."""
    errors: dict[str, list[str]] = {}
    ontology_dir = repo_root / "ontologies"
    if not ontology_dir.exists():
        return errors
    for f in sorted(ontology_dir.glob("*.ontology.yaml")):
        try:
            load_yaml_strict(f)
        except DuplicateKeyError as e:
            errors.setdefault(f.name, []).append(f"  - {e}")
        except yaml.YAMLError:
            continue
    return errors


def check_corpus(corpus: dict[str, dict]) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for oid, info in corpus.items():
        file_errors: list[str] = []
        ancestors = ancestor_namespaces(oid, corpus)
        for path, own in info["namespaces"].items():
            ancestor = ancestors.get(path)
            if ancestor is not None and ancestor.get("type_hint") != own.get("type_hint"):
                file_errors.append(
                    f"  - namespace '{path}': type_hint '{own.get('type_hint')}' here "
                    f"conflicts with type_hint '{ancestor.get('type_hint')}' declared by "
                    f"an ontology this one extends"
                )
            replaces = own.get("replaces")
            if (
                isinstance(replaces, str)
                and replaces
                and replaces not in ancestors
                and replaces not in info["namespaces"]
            ):
                file_errors.append(
                    f"  - namespace '{path}': replaces '{replaces}', which is not "
                    f"declared by this ontology or any it extends"
                )
        if file_errors:
            errors[info["file"]] = file_errors
    return errors


def main():
    repo_root = Path(__file__).parent.parent

    dup_errors = check_duplicate_keys(repo_root)
    corpus = load_corpus(repo_root)
    consistency_errors = check_corpus(corpus)

    all_errors: dict[str, list[str]] = {}
    for file_name, errs in dup_errors.items():
        all_errors.setdefault(file_name, []).extend(errs)
    for file_name, errs in consistency_errors.items():
        all_errors.setdefault(file_name, []).extend(errs)

    if all_errors:
        print("Namespace consistency validation FAILED:")
        for file_name, errs in sorted(all_errors.items()):
            print(f"\n{file_name}:")
            for err in errs:
                print(err)
        sys.exit(1)
    else:
        print("All ontology namespaces validated successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
