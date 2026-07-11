#!/usr/bin/env python3
"""Regression tests for scripts/validate-ontologies.py and
scripts/validate-namespaces.py: every check the CI gate relies on gets at
least one deliberately-broken fixture proving it actually fails closed, per
this repo's "every new gate gets a fixture proving it gates" convention
(see issue #52/#53).

Stdlib-only (unittest) -- this repo has no existing Python test runner, so
this avoids introducing one just to cover two small scripts. Run directly:
    python3 scripts/tests/test_ontology_validation.py
"""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


def _load(module_name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS_DIR / file_name)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_ontologies = _load("validate_ontologies", "validate-ontologies.py")
validate_namespaces = _load("validate_namespaces", "validate-namespaces.py")


class SubtypeOfIntegrityTests(unittest.TestCase):
    """validate-ontologies.py's graph checks -- no JSON Schema validator can
    express these, so they need their own coverage independent of ajv."""

    def test_self_reference_fails_closed(self):
        ontology = {"entity_types": [{"name": "widget", "subtype_of": ["widget"]}]}
        visible = validate_ontologies._type_info(ontology)
        errors = validate_ontologies.check_subtype_of(ontology, visible)
        self.assertTrue(any("cannot reference itself" in e for e in errors), errors)

    def test_missing_parent_fails_closed(self):
        ontology = {"entity_types": [{"name": "widget", "subtype_of": ["nonexistent"]}]}
        errors = validate_ontologies.check_subtype_of(ontology, {})
        self.assertTrue(any("is not a declared" in e for e in errors), errors)

    def test_substitutability_violation_fails_closed(self):
        ontology = {
            "entity_types": [
                {
                    "name": "child",
                    "subtype_of": ["parent"],
                    "schema": {"required": ["a"]},  # missing parent's required "b"
                }
            ]
        }
        visible = {"parent": {"required": {"a", "b"}, "subtype_of": []}}
        errors = validate_ontologies.check_subtype_of(ontology, visible)
        self.assertTrue(any("missing parent field" in e for e in errors), errors)

    def test_valid_subtype_passes(self):
        ontology = {
            "entity_types": [
                {"name": "child", "subtype_of": ["parent"], "schema": {"required": ["a", "b"]}}
            ]
        }
        visible = {"parent": {"required": {"a"}, "subtype_of": []}}
        errors = validate_ontologies.check_subtype_of(ontology, visible)
        self.assertEqual(errors, [])

    def test_missing_from_corpus_falls_back_to_local_types(self):
        # oid isn't a key in `corpus` at all (e.g. an id collision left this file's
        # entry overwritten) -- validate_ontology must not treat every locally
        # declared parent as unresolvable just because visible_types(oid, {}) == {}.
        ontology = {
            "ontology": {"id": "orphaned"},
            "entity_types": [
                {"name": "child", "subtype_of": ["parent"], "schema": {"required": ["a"]}},
                {"name": "parent", "schema": {"required": ["a"]}},
            ],
        }
        empty_corpus: dict = {}
        oid = ontology["ontology"]["id"]
        visible = validate_ontologies.visible_types(oid, empty_corpus)
        self.assertEqual(visible, {})  # confirms the scenario this guards against
        if not visible:
            visible = validate_ontologies._type_info(ontology)
        errors = validate_ontologies.check_subtype_of(ontology, visible)
        self.assertEqual(errors, [])

    def test_local_cycle_fails_closed(self):
        # a.subtype_of b, b.subtype_of a -- both declared in the SAME ontology. Per
        # check_subtype_of's own comment, cycle detection is intentionally scoped to
        # local types only (extends is one-way, so a cycle can never legitimately
        # span the ancestor boundary -- see the next test for why).
        ontology = {
            "entity_types": [
                {"name": "a", "subtype_of": ["b"]},
                {"name": "b", "subtype_of": ["a"]},
            ]
        }
        visible = validate_ontologies._type_info(ontology)
        errors = validate_ontologies.check_subtype_of(ontology, visible)
        self.assertTrue(any("cycle" in e for e in errors), errors)

    def test_ancestor_referencing_descendant_only_type_fails_as_missing_parent(self):
        # An ancestor's subtype_of can never resolve to a type only a descendant
        # declares (extends is one-way) -- this is WHY a subtype_of cycle can't
        # span the extends boundary: the ancestor side already fails independently,
        # on its own validation, before a "cycle" could ever form across repos/files.
        base_ontology = {"entity_types": [{"name": "b", "subtype_of": ["a"]}]}
        visible = validate_ontologies._type_info(base_ontology)  # base has no extends
        errors = validate_ontologies.check_subtype_of(base_ontology, visible)
        self.assertTrue(any("is not a declared" in e for e in errors), errors)


class AjvWrapperTests(unittest.TestCase):
    """Proves the ajv-validate.mjs wrapper (deliberately not ajv-cli -- see its
    own docstring) actually gates on real schema violations."""

    SCHEMA = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["ontology"],
        "properties": {
            "ontology": {
                "type": "object",
                "required": ["id"],
                "properties": {"id": {"type": "string", "pattern": "^[a-z][a-z0-9-]*$"}},
            }
        },
    }

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.schema_path = self.tmpdir / "schema.json"
        self.schema_path.write_text(json.dumps(self.SCHEMA))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_invalid_id_pattern_fails_closed(self):
        errors = validate_ontologies._ajv_validate({"ontology": {"id": "Not_Valid"}}, self.schema_path)
        self.assertTrue(errors, "expected ajv wrapper to reject a bad id pattern")

    def test_valid_document_passes(self):
        errors = validate_ontologies._ajv_validate({"ontology": {"id": "valid-id"}}, self.schema_path)
        self.assertEqual(errors, [])


class NamespaceConsistencyTests(unittest.TestCase):
    """validate-namespaces.py's fresh checks (see its module docstring for why
    this isn't a port of MIF's retired memory-namespace script)."""

    def test_malformed_yaml_fails_closed_standalone(self):
        # check_duplicate_keys previously silently swallowed any yaml.YAMLError
        # (not just DuplicateKeyError), so a syntactically broken ontology file
        # made validate-namespaces.py exit 0 when run standalone -- it just
        # vanished from the corpus instead of being reported as broken.
        tmpdir = Path(tempfile.mkdtemp())
        try:
            ontology_dir = tmpdir / "ontologies"
            ontology_dir.mkdir()
            (ontology_dir / "broken.ontology.yaml").write_text("namespaces: [unterminated\n")
            errors = validate_namespaces.check_duplicate_keys(tmpdir)
            self.assertIn("broken.ontology.yaml", errors)
            self.assertTrue(any("YAML parse error" in e for e in errors["broken.ontology.yaml"]))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_duplicate_namespace_key_fails_closed(self):
        text = """
namespaces:
  semantic:
    children:
      foo:
        type_hint: semantic
      foo:
        type_hint: semantic
"""
        with self.assertRaises(validate_namespaces.DuplicateKeyError):
            import yaml

            yaml.load(text, Loader=validate_namespaces._UniqueKeyLoader)

    def test_cross_ontology_type_hint_conflict_fails_closed(self):
        corpus = {
            "base": {
                "file": "base.ontology.yaml",
                "extends": [],
                "namespaces": {"semantic/foo": {"type_hint": "semantic", "replaces": None}},
            },
            "child": {
                "file": "child.ontology.yaml",
                "extends": ["base"],
                "namespaces": {"semantic/foo": {"type_hint": "episodic", "replaces": None}},
            },
        }
        errors = validate_namespaces.check_corpus(corpus)
        self.assertIn("child.ontology.yaml", errors)
        self.assertTrue(any("conflicts with type_hint" in e for e in errors["child.ontology.yaml"]))

    def test_matching_type_hint_across_extends_passes(self):
        corpus = {
            "base": {
                "file": "base.ontology.yaml",
                "extends": [],
                "namespaces": {"semantic/foo": {"type_hint": "semantic", "replaces": None}},
            },
            "child": {
                "file": "child.ontology.yaml",
                "extends": ["base"],
                "namespaces": {"semantic/foo": {"type_hint": "semantic", "replaces": None}},
            },
        }
        errors = validate_namespaces.check_corpus(corpus)
        self.assertEqual(errors, {})

    def test_dangling_replaces_fails_closed(self):
        corpus = {
            "solo": {
                "file": "solo.ontology.yaml",
                "extends": [],
                "namespaces": {
                    "semantic/new": {"type_hint": "semantic", "replaces": "semantic/nonexistent"}
                },
            }
        }
        errors = validate_namespaces.check_corpus(corpus)
        self.assertIn("solo.ontology.yaml", errors)
        self.assertTrue(any("not declared" in e for e in errors["solo.ontology.yaml"]))


if __name__ == "__main__":
    unittest.main()
