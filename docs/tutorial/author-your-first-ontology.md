---
id: tutorial-author-your-first-ontology
type: procedural
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: tutorials/ontology-corpus
title: Author Your First Ontology
tags:
  - tutorial
  - ontology
  - mif
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
relationships:
  - type: relates-to
    target: ../how-to/add-a-domain-ontology.md
  - type: relates-to
    target: ../explanation/ontology-model.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Author Your First Ontology
  entity_type: tutorial
---

# Author Your First Ontology

By the end of this lesson you will have written a small domain ontology by hand.
It builds on the Modeled Information Format (MIF) base ontologies, declares its
own namespace, and defines a single entity type that composes traits it inherited
rather than redefining them. You will read the same file two ways: the YAML a
person reads, and the JSON-LD a parser resolves. They are the same model.

You will not run any tool. The corpus is authored by hand, and this lesson is
about writing and reading the YAML, not about validation.

## Prerequisites

- A text editor.
- The two base ontologies open for reference (you will not edit them):
  [`mif-base.ontology.yaml`](../../ontologies/mif-base.ontology.yaml) and
  [`shared-traits.ontology.yaml`](../../ontologies/shared-traits.ontology.yaml).
- A new, empty file named `garden-sensors.ontology.yaml`.

You are building a `garden-sensors` ontology: one entity type for a soil sensor
that records measurements, sits at a location, and tracks where its data came
from.

## Step 1: Declare the ontology and extend the base

Open `garden-sensors.ontology.yaml` and type the header:

```yaml
---
ontology:
  id: garden-sensors
  version: "0.1.0"
  description: "A tiny ontology for garden soil sensors"
  extends:
    - mif-base
    - shared-traits
```

The `extends:` list is doing the work. Your ontology now inherits every namespace,
trait, and relationship those two define. `mif-base` brings the `provenance`
trait; `shared-traits` brings `measured` and `located`. You will compose all
three in Step 3 without copying a single field.

**Checkpoint.** Your file now opens with one `ontology:` block whose `extends:`
names `mif-base` and `shared-traits`. The order matters: a later entry wins on a
name conflict.

## Step 2: Declare one namespace

A namespace is the path a record files itself under. The base ontologies already
define the three top-level namespaces: `_semantic`, `_episodic`, `_procedural`.
You add one child of your own. Append this:

```yaml
namespaces:
  _semantic:
    description: "Facts about garden hardware"
    type_hint: semantic
    children:
      sensors:
        description: "Soil sensors and the readings they hold"
        type_hint: semantic
```

This declares the path `_semantic/sensors`. A soil-sensor record will name that
path so a reader (human or parser) knows it is declarative knowledge about a
sensor.

**Checkpoint.** Your `namespaces:` block declares `_semantic` with a child
`sensors`. You did not redefine `_episodic` or `_procedural`; they are inherited.

## Step 3: Define one entity type that composes inherited traits

Entity types are the one thing `extends:` does *not* hand you, each ontology
defines its own. That is the point of this step: you declare `soil-sensor` and
list the inherited traits it should carry. Append this:

```yaml
entity_types:
  - name: soil-sensor
    description: "A soil sensor that records measurements at a known location"
    base: semantic
    traits:
      - measured
      - located
      - provenance
    schema:
      required:
        - name
      properties:
        name:
          type: string
          description: "Human-readable sensor name"
        sensor_id:
          type: string
          description: "Hardware identifier"
```

`base: semantic` says a `soil-sensor` is declarative knowledge: a thing that is,
not an event or a procedure. The `traits:` list names three mixins by their bare
names: `measured` and `located` from `shared-traits`, `provenance` from
`mif-base`. You do not restate their fields. The `schema:` block adds only what
is specific to your domain: a required `name` and an optional `sensor_id`.

**Checkpoint.** Your `entity_types:` list holds exactly one entry, `soil-sensor`,
with three trait names and a two-property `schema`. That is the complete file.

## Step 4: Read it the way a parser does

You wrote YAML for a person. A parser reads the same model as JSON-LD, where every
name resolves to a stable identifier. The MIF spec repo generates that projection;
for a `soil-sensor` entity type your file resolves to a node like this:

```json
{
  "@id": "mif:entityType/soil-sensor",
  "@type": "mif:EntityType",
  "name": "soil-sensor",
  "base": "semantic",
  "traits": [
    "mif:trait/measured",
    "mif:trait/located",
    "mif:trait/provenance"
  ],
  "schema": {
    "required": ["name"],
    "properties": {
      "name": { "type": "string", "description": "Human-readable sensor name" },
      "sensor_id": { "type": "string", "description": "Hardware identifier" }
    }
  }
}
```

Read the two side by side. Where you typed `measured`, the parser holds
`mif:trait/measured` and follows your `extends:` chain to the definition in
`shared-traits`. Where you typed `base: semantic`, the parser holds the typed
identifier for declarative knowledge. The `schema` you wrote survives the trip
field for field. One model. A person reads the left column; a parser resolves the
right. Neither is a translation of the other.

## What you learned

- An ontology declares itself with `ontology: { id, version, extends }`, and
  `extends:` pulls in the namespaces, traits, and relationships of the ontologies
  it names.
- Namespaces give a record its filing path; you added `_semantic/sensors` without
  touching the inherited triad.
- Entity types are *not* inherited, you define your own and compose inherited
  traits (`measured`, `located`, `provenance`) by name instead of copying fields.
- The YAML a person reads and the JSON-LD a parser resolves are the same model.

You wrote a valid `garden-sensors` ontology and can read both halves of it. The
corpus is authored by hand here; the canonical schema check and the
markdown-to-JSON-LD generation live in the MIF spec repo's `scripts/` and run in
that repo's CI.

Next:

- Add another ontology to the corpus as a flat `ontologies/<name>.ontology.yaml`
  file (and its generated `.ontology.jsonld`): see
  [Add a domain ontology](../how-to/add-a-domain-ontology.md).
- Understand *why* the model is shaped this way (the triad, `extends:`, and why
  entity types stay local) in [The ontology model](../explanation/ontology-model.md).

## Related

- [Add a domain ontology](../how-to/add-a-domain-ontology.md)
- [The ontology model](../explanation/ontology-model.md)
- [`mif-base.ontology.yaml`](../../ontologies/mif-base.ontology.yaml)
- [`shared-traits.ontology.yaml`](../../ontologies/shared-traits.ontology.yaml)
