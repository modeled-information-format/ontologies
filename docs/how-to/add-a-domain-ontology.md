---
id: how-to-add-a-domain-ontology
type: procedural
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: how-to/ontology-corpus
title: Add a Domain Ontology to the Corpus
tags:
  - how-to
  - ontology
  - mif
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
relationships:
  - type: relates-to
    target: ../reference/ontology-corpus.md
  - type: relates-to
    target: ../tutorial/author-your-first-ontology.md
  - type: relates-to
    target: ./submit-an-ontology.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Add a Domain Ontology to the Corpus
  entity_type: how-to-guide
---

# Add a domain ontology to the corpus

You have a domain the corpus does not yet cover and a set of entity types you
want to model. This guide adds one ontology to `ontologies/`. The corpus is
flat: each ontology is a single `<name>.ontology.yaml` source file with a
committed `<name>.ontology.jsonld` projection beside it, both directly under
`ontologies/`. Your ontology declares `extends:`, so you define only what is
specific to your domain and inherit the rest from the foundations.

The running example is a `customer-support` ontology. Substitute your own
`<name>` (lowercase, hyphenated) throughout. MIF is the Modeled Information
Format.

## Prerequisites

- A working clone of `modeled-information-format/ontologies` (this repo).
- A clone of the sibling `modeled-information-format/MIF` spec repo, which holds
  the projector and validators this repo does not vendor. Its Python deps:
  `pip install pyyaml jsonschema`.
- Familiarity with the base model: the knowledge triad (`_semantic`,
  `_episodic`, `_procedural`), core traits, and trait inheritance via `extends`.
  See [the ontology model](../explanation/ontology-model.md) if you need it.

## 1. Create the ontology file

Each ontology is one flat file under `ontologies/`, named for its `id`:

```bash
touch ontologies/customer-support.ontology.yaml
```

This YAML is the source of record. The matching `customer-support.ontology.jsonld`
is generated in step 3 and committed beside it.

## 2. Author the ontology

Declare the `ontology:` header first with `id`, `version`, and `extends`. The
corpus foundations are `mif-base` (the knowledge triad and core traits) and
`shared-traits` (cross-domain trait mixins). Add any domain `namespaces:` under
the inherited triad, then define `entity_types:` that compose inherited traits.

`ontologies/customer-support.ontology.yaml`:

```yaml
ontology:
  id: customer-support
  version: "0.1.0"
  description: "Customer-support domain ontology: tickets, known issues, and escalation procedures"
  schema_url: >-
    https://mif-spec.dev/schema/ontology/ontology.schema.json
  extends:
    - mif-base        # core traits: timestamped, confidence, provenance
    - shared-traits   # cross-domain mixins: lifecycle, owned, scored, tagged, reviewed, and more
# Domain namespaces (added under the inherited base-type triad).
namespaces:
  semantic:
    children:
      known_issues:
        description: "Known product defects and workarounds"
        type_hint: semantic
  episodic:
    children:
      tickets:
        description: "Support tickets and their handling history"
        type_hint: episodic
# Entity types: domain-specific. Each names its base type and composes
# inherited traits. Entity types are NOT inherited, so define your own.
entity_types:
  - name: known-issue
    description: "A recurring product defect with a documented workaround"
    base: semantic
    traits:
      - tagged        # from shared-traits
      - provenance    # from mif-base
    schema:
      required:
        - title
        - workaround
      properties:
        title:
          type: string
        workaround:
          type: string
        affected_versions:
          type: array
          items:
            type: string
  - name: support-ticket
    description: "A single customer support request and its resolution"
    base: episodic
    traits:
      - lifecycle     # from shared-traits: status + status_history
      - owned         # from shared-traits: assignee/steward
      - timestamped   # from mif-base
    schema:
      required:
        - subject
        - channel
      properties:
        subject:
          type: string
        channel:
          type: string
          enum:
            - email
            - chat
            - phone
        resolution:
          type: string
  - name: escalation-runbook
    description: "Step-by-step procedure for escalating a ticket"
    base: procedural
    traits:
      - reviewed      # from shared-traits: review/approval workflow
    schema:
      required:
        - title
        - procedure
      properties:
        title:
          type: string
        procedure:
          type: array
          items:
            type: object
            properties:
              step:
                type: integer
              action:
                type: string
# Relationships and discovery patterns are optional; inherited ones still apply.
relationships:
  resolved_by:
    description: "A ticket is resolved by following a runbook"
    from:
      - support-ticket
    to:
      - escalation-runbook
    symmetric: false
```

The `base` of each entity type is unprefixed (`semantic`, `episodic`,
`procedural`); namespace paths keep the underscore prefix (`_semantic/...`).
Every name under `traits:` must resolve to a trait defined here or inherited
through the `extends` chain.

## 3. Generate the JSON-LD projection

Project the YAML to JSON-LD with the MIF spec repo's projector. This is the
parser's read of the same model: the same ontology a person reads in YAML and a
parser resolves in JSON-LD. The projector writes `<name>.ontology.jsonld` beside
the source file:

```bash
python /path/to/MIF/scripts/yaml2jsonld.py ontologies/customer-support.ontology.yaml
```

This writes `ontologies/customer-support.ontology.jsonld`. Commit both the YAML
and the JSON-LD; every ontology in the corpus carries its committed projection.

## 4. Validate against the ontology schema

The validators live in the MIF spec repo (`scripts/validate-ontologies.py` and
`scripts/validate-namespaces.py`), since MIF owns `ontology.schema.json`. MIF
authors no ontology content of its own (ADR-018), so both take a `--path <dir>`
argument pointing at the corpus to check, rather than scanning a tree inside
the MIF checkout. Point `--path` at this repo's own `ontologies/` directory so
your new file validates against the real `mif-base` and `shared-traits`
parents:

```bash
cd /path/to/MIF
python scripts/validate-ontologies.py --path /path/to/ontologies/ontologies
python scripts/validate-namespaces.py --path /path/to/ontologies/ontologies
```

A clean exit from both means the ontology is schema-conformant (`$id`
`https://mif-spec.dev/schema/ontology/ontology.schema.json`), its namespaces
resolve, and its entity-type subsumption (`subtype_of`) holds across the
`extends` chain.

Your ontology is complete. To propose it for inclusion in the published corpus,
follow [Submit an ontology](./submit-an-ontology.md).

## Related

- [Ontology corpus reference](../reference/ontology-corpus.md): the catalog of
  ontologies, foundations, and shared traits.
- [Author your first ontology](../tutorial/author-your-first-ontology.md): the
  learning-oriented walkthrough.
- [Submit an ontology](./submit-an-ontology.md): open an ontology for inclusion
  in the corpus.
