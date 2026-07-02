---
id: how-to-submit-an-ontology
type: procedural
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: how-to/ontology-corpus
title: Submit an Ontology to the Corpus
tags:
  - how-to
  - contributing
  - ontology
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
relationships:
  - type: relates-to
    target: ./add-a-domain-ontology.md
  - type: relates-to
    target: ../reference/ontology-corpus.md
  - type: relates-to
    target: ../decisions/0001-underscore-prefixed-base-namespaces.md
  - type: relates-to
    target: ../runbooks/release-the-corpus.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Submit an Ontology to the Corpus
  entity_type: how-to-guide
---

# Submit an Ontology to the Corpus

You have a domain ontology to add to the Modeled Information Format (MIF) corpus
at `modeled-information-format/ontologies`. This guide takes you from a branch to
a merged pull request to a tagged release. It assumes you have already written,
or are ready to write, the ontology itself. The authoring mechanics (namespaces,
trait composition, entity types, and how `extends` resolves) live in
[Add a domain ontology](./add-a-domain-ontology.md); follow that recipe, then
return here to submit.

The deliverable is two files, side by side, directly under `ontologies/`:

```text
ontologies/<your-domain>.ontology.yaml     # the source you author by hand
ontologies/<your-domain>.ontology.jsonld   # the projection a parser resolves
```

Ontologies are flat files. There is no per-ontology directory, no manifest
file, and no per-ontology README. The YAML is the source of record; the JSON-LD
is generated from it and committed beside it.

## Prerequisites

- A GitHub account and a fork of `modeled-information-format/ontologies`, or
  write access to a branch.
- A local checkout of the MIF spec repo (`modeled-information-format/MIF`) beside
  your corpus checkout. The `yaml2jsonld.py` projector, the validators, and the
  canonical `ontology.schema.json` all live there. This corpus repo has no
  `scripts/` directory of its own.
- The MIF repo's CI dependencies installed (`PyYAML` and `ajv-cli`); the MIF repo
  documents the exact pinned setup.
- A finished `<your-domain>.ontology.yaml` with its `id`, `version`, `extends`,
  namespaces, traits, and entity types decided. If you do not have one yet, start
  with [Add a domain ontology](./add-a-domain-ontology.md).

## Steps

### 1. Branch

```bash
git clone https://github.com/<you>/ontologies.git
cd ontologies
git checkout -b add-<your-domain>-ontology
```

### 2. Place the YAML source

Put your authored ontology directly under `ontologies/`, named for the domain:

```bash
cp <your-domain>.ontology.yaml ontologies/
```

The file declares its `ontology` block first (`id`, `version`, `description`, and
`extends` naming the parent ontology ids it builds on), then `namespaces`,
`traits`, and `entity_types`. The corpus foundations are `mif-base` and
`shared-traits`; `extends` names whichever parents your entity types compose
from. Do not duplicate the authoring recipe here. Come back from
[Add a domain ontology](./add-a-domain-ontology.md) with a finished YAML.

### 3. Generate the JSON-LD projection

The corpus commits each ontology twice: the `*.ontology.yaml` a person reads and
the `*.ontology.jsonld` a parser resolves. They are the same model, projected
losslessly from the YAML. Generate the projection from your MIF checkout:

```bash
python /path/to/MIF/scripts/yaml2jsonld.py \
  ontologies/<your-domain>.ontology.yaml
```

This writes `ontologies/<your-domain>.ontology.jsonld` beside the YAML. You will
commit both.

### 4. Validate locally

This is your conformance gate. The corpus repo's own CI runs supply-chain
security gates, not ontology validation (see step 6), so local validation against
the schema is what proves your ontology conforms.

MIF authors no ontology content of its own (ADR-018), so the validators take a
`--path <dir>` argument pointing at the corpus to check, rather than scanning a
tree inside the MIF checkout itself. Point `--path` at this repo's own
`ontologies/` directory so your new file validates against the real `mif-base`
and `shared-traits` parents:

```bash
cd /path/to/MIF

python scripts/validate-ontologies.py --path /path/to/ontologies/ontologies
python scripts/validate-namespaces.py --path /path/to/ontologies/ontologies
```

`validate-ontologies.py` checks each `*.ontology.yaml` against
`ontology.schema.json` (resolvable `$id`
`https://mif-spec.dev/schema/ontology/ontology.schema.json`), plus `subtype_of`
subsumption integrity across the whole corpus. `validate-namespaces.py`
confirms every namespace your entity types reference exists in the declared
ontologies. Each validator prints a success line and exits `0` when clean. Fix
anything they report before you open the pull request.

(`scripts/test_subtype_of.py` also lives in MIF, but only exercises the
`subtype_of` resolver against its own hardcoded fixtures; it does not check
your submission and does not take a `--path` argument.)

### 5. Commit the YAML and the JSON-LD together

```bash
git add ontologies/<your-domain>.ontology.yaml \
        ontologies/<your-domain>.ontology.jsonld
git commit -m "Add <your-domain> ontology"
```

Commit both files in one change. The YAML and the JSON-LD are the same model read
two ways; a pull request that commits one without the other is incomplete.

### 6. Open a pull request

```bash
git push origin add-<your-domain>-ontology
```

Open a pull request against `main`. Describe the domain, the `id` and `version`,
and which parent ontologies it extends.

The corpus pipeline is the org's attested release architecture: supply-chain
security gating, not ontology validation. On a pull request to `main` these gates
run:

| Gate (job) | Workflow | What it checks |
| --- | --- | --- |
| `pin-check` | `ci.yml` | Every `uses:` is pinned to a full 40-character commit SHA |
| `lint` | `ci.yml` | Repository hygiene (TODO/FIXME marker scan) |
| `validate-workflows` | `ci.yml` | Workflow YAML is well-formed (`actionlint`) |
| `sast` | `quality-gates.yml` | Static analysis (CodeQL) |
| `sca` | `quality-gates.yml` | Dependency vulnerabilities (OSV) |
| `trivy` | `quality-gates.yml` | IaC and license scan (Trivy) |

The `posture` gate (Scorecard, in `quality-gates.yml`) runs on push to `main` and
weekly, not on the pull request. Every action these workflows call is SHA-pinned,
and `pin-check` fails the build if any reference is a tag or branch instead of a
commit SHA. None of these gates inspect your ontology. That is why step 4 is the
conformance gate.

### 7. Review and merge

A maintainer reviews the pull request and merges it to `main`. Your ontology is
now in the corpus source tree, but not yet released.

### 8. Release the corpus

The corpus publishes when a maintainer pushes a `vX.Y.Z` tag, which triggers the
attested release pipeline (`release.yml`): build, attest provenance and SBOM,
fail-closed verification, then a tag-gated publish. Follow
[Release the corpus](../runbooks/release-the-corpus.md) for the procedure.

Your ontology is submitted: authored, generated, validated, committed with its
projection, reviewed, merged, and released.

## Submission checklist

- [ ] `ontologies/<your-domain>.ontology.yaml` is present, with `extends`
      declared (the parents your entity types compose from).
- [ ] Namespace references are underscore-correct: base-type namespaces carry the
      `_` prefix (`_semantic`, `_episodic`, `_procedural`); domain namespaces do
      not. See
      [Underscore-prefixed base namespaces](../decisions/0001-underscore-prefixed-base-namespaces.md).
- [ ] `ontologies/<your-domain>.ontology.jsonld` is regenerated and committed
      beside the YAML.
- [ ] No `pack.json`, no per-ontology directory, and no per-ontology README; the
      submission is the two flat files only.
- [ ] `validate-ontologies.py` and `validate-namespaces.py` pass against your
      ontology.
- [ ] Pull request gates are green.

## Related

- [Add a domain ontology](./add-a-domain-ontology.md): the authoring recipe for
  the ontology you submit here.
- [Ontology corpus](../reference/ontology-corpus.md): what the corpus contains and
  how its ontologies are organized.
- [Underscore-prefixed base namespaces](../decisions/0001-underscore-prefixed-base-namespaces.md):
  the decision behind the `_` prefix on base-type namespaces.
- [Release the corpus](../runbooks/release-the-corpus.md): cutting the `vX.Y.Z`
  tag that publishes a merged submission.
