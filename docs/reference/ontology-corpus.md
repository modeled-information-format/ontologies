---
id: reference-ontology-corpus
type: semantic
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: reference/ontology-corpus
title: Ontology Corpus Reference
tags:
  - reference
  - ontology
  - corpus
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
relationships:
  - type: relates-to
    target: ../explanation/ontology-model.md
  - type: relates-to
    target: ../how-to/add-a-domain-ontology.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Ontology Corpus Reference
  entity_type: reference-document
---

# Ontology Corpus Reference

The MIF (Modeled Information Format) ontology corpus is the set of ontologies
maintained in this repository. Every ontology is a flat file directly under
`ontologies/`. Each `ontologies/<name>.ontology.yaml` is the source of record, and
each has a committed `ontologies/<name>.ontology.jsonld` projection beside it,
generated from the YAML. There are no subdirectories, and there is no separate
examples tree.

## Catalog

Four base ontologies (`mif-base`, `shared-traits`, `engineering-base`,
`mif-generic`) plus fourteen domain ontologies, eighteen in all. The `version`
column is the YAML `ontology.version` field.

| Ontology id | Version | Path | Description |
| --- | --- | --- | --- |
| `mif-base` | 1.0.0 | `ontologies/mif-base.ontology.yaml` | Foundation: the knowledge triad namespaces and core traits. |
| `shared-traits` | 1.0.0 | `ontologies/shared-traits.ontology.yaml` | Foundation: cross-domain reusable trait mixins. |
| `engineering-base` | 0.1.0 | `ontologies/engineering-base.ontology.yaml` | Intermediate engineering supertypes (`versioned`, `documented`, `dated`, `cited`) the engineering domains extend. |
| `mif-generic` | 1.0.0 | `ontologies/mif-generic.ontology.yaml` | Generic built-in entity types, always enabled for all topics. |
| `biology-research-lab` | 0.1.0 | `ontologies/biology-research-lab.ontology.yaml` | Biology research lab entities with full lifecycle traits. |
| `data-engineering` | 0.2.0 | `ontologies/data-engineering.ontology.yaml` | Data engineering domain entities. |
| `market-research` | 0.1.0 | `ontologies/market-research.ontology.yaml` | Segments, competitors, sizing, forces, and market intelligence. |
| `mif-docs` | 1.0.0 | `ontologies/mif-docs.ontology.yaml` | Document genres of the mif-docs suite and the relationships connecting them. |
| `observability` | 0.1.0 | `ontologies/observability.ontology.yaml` | Services, telemetry signals, ownership registries, and roadmap signals. |
| `platform-engineering` | 0.1.0 | `ontologies/platform-engineering.ontology.yaml` | Internal developer portals, portal plugins, software templates, golden paths, and typed integrations. |
| `psycholinguistics` | 0.1.0 | `ontologies/psycholinguistics.ontology.yaml` | Psychological and linguistic constructs, stylometric and psychometric features. |
| `regenerative-agriculture` | 0.1.0 | `ontologies/regenerative-agriculture.ontology.yaml` | Regenerative agriculture entities with ecosystem coverage. |
| `regenerative-agriculture-research` | 0.3.1 | `ontologies/regenerative-agriculture-research.ontology.yaml` | Research observations about regenerative farming practices. |
| `regulatory-legal` | 0.1.0 | `ontologies/regulatory-legal.ontology.yaml` | Acts, obligations, authorities, jurisdictions, contracts, and sanctions. |
| `scientific` | 0.1.0 | `ontologies/scientific.ontology.yaml` | Studies, methods, data, and provenance. |
| `software-engineering` | 0.5.0 | `ontologies/software-engineering.ontology.yaml` | Software incidents and SDLC operational procedures. |
| `software-security` | 0.1.0 | `ontologies/software-security.ontology.yaml` | Vulnerabilities, weaknesses, controls, threat actors, malware, and indicators of compromise. |
| `trend-analysis` | 0.1.0 | `ontologies/trend-analysis.ontology.yaml` | Signals, drivers, trends, scenarios, and forecasts. |

## Namespace triad

`mif-base` defines three top-level namespaces, each prefixed with an underscore to
mark it as a base-type namespace. Each carries a `type_hint` and a set of children.
The path format is `_<top-level>/<child>` (for example, `_semantic/decisions`).

| Namespace | `type_hint` | Description |
| --- | --- | --- |
| `_semantic` | `semantic` | Facts, concepts, relationships (declarative knowledge). |
| `_episodic` | `episodic` | Events, experiences, timelines (time-bound records). |
| `_procedural` | `procedural` | Step-by-step processes (how-to knowledge). |

| Child path | `type_hint` | Description |
| --- | --- | --- |
| `_semantic/decisions` | `semantic` | Architectural choices with rationale. |
| `_semantic/knowledge` | `semantic` | APIs, context, learnings, security (factual knowledge). |
| `_semantic/entities` | `semantic` | Entity definitions: technologies, components, systems. |
| `_semantic/preferences` | `semantic` | User preferences, settings, configuration choices. |
| `_episodic/incidents` | `episodic` | Production issues, outages, postmortems. |
| `_episodic/sessions` | `episodic` | Debug sessions, work sessions, meeting notes. |
| `_episodic/blockers` | `episodic` | Impediments, issues preventing progress. |
| `_procedural/runbooks` | `procedural` | Operational procedures, SOPs, playbooks. |
| `_procedural/patterns` | `procedural` | Code conventions, best practices, testing strategies. |
| `_procedural/migrations` | `procedural` | Migration steps, upgrade procedures, data transformations. |

A `type_hint` value is one of `semantic`, `episodic`, or `procedural`. Domain
ontologies add their own namespaces under these top-level paths.

## Trait catalog

Traits are reusable field mixins composed into entity types. Core traits come from
`mif-base`; shared traits come from `shared-traits` (which extends `mif-base`).

### Core traits (`mif-base`)

| Trait | Fields | Description |
| --- | --- | --- |
| `timestamped` | `created_at` (date-time), `updated_at` (date-time) | Adds creation and update timestamps. |
| `confidence` | `confidence` (number, 0.0 to 1.0) | Adds a confidence score for freshness and validity tracking. |
| `provenance` | `source` (string), `author` (string) | Adds source tracking. |

### Shared traits (`shared-traits`)

Twenty traits, grouped as they are in the source file.

| Group | Trait | Key fields | Description |
| --- | --- | --- | --- |
| Lifecycle | `lifecycle` | `status`, `status_history[]` | Lifecycle state tracking with transitions. |
| Lifecycle | `renewable` | `effective_date`, `expiration_date`, `renewal_date`, `auto_renew` | Renewal and expiration tracking for time-limited entities. |
| Compliance | `auditable` | `audit_log[]`, `last_audit_date`, `next_audit_date`, `audit_status` | Audit trail and compliance tracking. |
| Compliance | `certified` | `certifications[]` | Certification and accreditation tracking. |
| Compliance | `regulated` | `regulations[]` | Regulatory compliance tracking. |
| Geographic | `located` | `location` (address, city, state, country, postal_code, coordinates) | Physical location data. |
| Geographic | `bounded` | `boundary` (type, coordinates, area_unit, area_value) | Geographic boundary and area data. |
| Stakeholder | `owned` | `owner`, `steward` | Ownership and responsibility tracking. |
| Stakeholder | `contactable` | `contacts[]` | Contact information. |
| Financial | `budgeted` | `budget` (allocated, spent, remaining, currency, fiscal_year), `cost_center` | Budget and financial tracking. |
| Financial | `transactional` | `transactions[]` | Transaction and payment tracking. |
| Temporal | `scheduled` | `schedule` (start_date, end_date, recurrence, timezone) | Scheduling and calendar integration. |
| Temporal | `seasonal` | `season`, `cycle_start`, `cycle_end`, `cycle_type` | Seasonal and cyclical timing. |
| Measurement | `measured` | `measurements[]` | Quantitative measurement data. |
| Measurement | `scored` | `scores[]` | Scoring and rating data. |
| Classification | `categorized` | `category`, `subcategory`, `taxonomy[]` | Hierarchical categorization. |
| Classification | `tagged` | `tags[]`, `labels` | Flexible tagging. |
| Asset | `inventoried` | `inventory_id`, `serial_number`, `quantity`, `unit`, `location_code`, `last_inventory_date` | Inventory tracking. |
| Asset | `maintainable` | `maintenance_schedule`, `last_maintenance`, `next_maintenance`, `maintenance_log[]` | Maintenance scheduling. |
| Quality | `reviewed` | `review_status`, `reviewer`, `review_date`, `review_notes`, `approval_chain[]` | Review and approval workflow. |
| Quality | `quality_controlled` | `qc_status`, `qc_checkpoints[]` | Quality control checkpoints. |

Domain ontologies define additional traits of their own and compose any of the
above into their entity types.

## Ontology file schema

Each `ontologies/<name>.ontology.yaml` declares the following top-level blocks.

```yaml
ontology:
  id: <ontology-id>
  version: "<semver>"
  description: "<one sentence>"
  extends:              # optional
    - <parent-ontology-id>
  schema_url: >-        # optional
    https://mif-spec.dev/schema/ontology/ontology.schema.json

namespaces:
  <name>:
    description: "..."
    type_hint: semantic | episodic | procedural
    children:
      <child>:
        description: "..."
        type_hint: semantic | episodic | procedural

traits:
  <trait-name>:
    description: "..."
    fields:
      <field>:
        type: string | number | boolean | array | object
        # plus format, enum, items, properties as applicable

entity_types:
  - name: <entity-type-name>
    description: "..."
    base: semantic | episodic | procedural
    traits:
      - <trait-name>
    schema:
      required:
        - <field>
      properties:
        <field>:
          type: <type>

relationships:
  <relationship-name>:
    description: "..."
    from: []
    to: []
    symmetric: true | false

discovery:
  enabled: true | false
  confidence_threshold: <number>
  content_patterns: [...]
  file_patterns: [...]
```

### Block fields

| Block | Field | Type | Notes |
| --- | --- | --- | --- |
| `ontology` | `id` | string | Stable ontology identifier. |
| `ontology` | `version` | string | SemVer, quoted. |
| `ontology` | `description` | string | One sentence. |
| `ontology` | `extends` | list of ontology ids | Optional. Names parent ontologies this ontology builds on. |
| `ontology` | `schema_url` | string | Optional. Resolvable URL of `ontology.schema.json`. |
| `namespaces` | `<name>` | map | `description`, `type_hint`, optional `children`. |
| `traits` | `<trait-name>` | map | `description` and a `fields` map. |
| `entity_types` | `name` | string | Entity type identifier. |
| `entity_types` | `base` | enum | One of `semantic`, `episodic`, `procedural`. |
| `entity_types` | `traits` | list | Trait names composed into the type. |
| `entity_types` | `schema` | map | JSON Schema fragment with `required` and `properties`. |

### Inheritance via `extends`

`extends` names one or more parent ontology ids. The base ontologies are
`mif-base` (the root), `shared-traits`, `engineering-base`, and `mif-generic`;
the thirteen domain ontologies build on these.

| Inherited through `extends` | Not inherited |
| --- | --- |
| `traits` | `entity_types` |
| `relationships` | |
| `namespaces` | |
| `discovery` patterns | |

Each ontology declares its own `entity_types`, composing inherited traits. When
multiple parents are listed, a later `extends` entry overrides an earlier one on
conflict.

The `extends` declared by each domain ontology:

| Ontology | `extends` |
| --- | --- |
| `biology-research-lab` | `mif-base`, `shared-traits` |
| `data-engineering` | `engineering-base` |
| `market-research` | `mif-base`, `shared-traits` |
| `mif-docs` | `mif-base` |
| `observability` | `engineering-base`, `mif-generic` |
| `platform-engineering` | `engineering-base` |
| `psycholinguistics` | `engineering-base`, `mif-generic` |
| `regenerative-agriculture` | `mif-base`, `shared-traits` |
| `regenerative-agriculture-research` | `engineering-base`, `mif-generic` |
| `regulatory-legal` | `mif-base`, `shared-traits` |
| `scientific` | `mif-base`, `shared-traits` |
| `software-engineering` | `engineering-base` |
| `software-security` | `mif-base`, `shared-traits` |
| `trend-analysis` | `mif-base`, `shared-traits` |

`shared-traits` and `mif-generic` extend `mif-base`; `engineering-base` extends
`mif-base` and `shared-traits`; `mif-base` declares no `extends`.

## Declaring conformance in a memory

A memory references the ontology it conforms to with an `ontology` block (`id`,
`version`, optional `uri`) and a `namespace` path. The same declaration works in
YAML frontmatter and in the JSON-LD projection.

```yaml
ontology:
  id: mif-base
  version: "1.0.0"
  uri: https://mif-spec.dev/schema/ontology/ontology.schema.json
namespace: _semantic/decisions
```

The `namespace` value is one of the triad child paths (or a domain namespace) the
declared ontology defines.

## Tooling and schema pointers

| Item | Value |
| --- | --- |
| Source of record | `ontologies/<name>.ontology.yaml` (hand-authored). |
| Projection | `ontologies/<name>.ontology.jsonld` (generated, committed beside the YAML). |
| Generator | `scripts/yaml2jsonld.py --all --path <dir>` in the `modeled-information-format/MIF` spec repo. |
| Validators | `scripts/validate-ontologies.py --path <dir>`, `scripts/validate-namespaces.py --path <dir>` (in the MIF spec repo; `--path` points at this repo's `ontologies/` directory, since MIF authors no ontology content of its own — ADR-018). `scripts/test_subtype_of.py` also lives in MIF but only exercises its own hardcoded fixtures; it does not check this corpus and takes no `--path`. |
| Canonical schema | `ontology.schema.json`, `$id` `https://mif-spec.dev/schema/ontology/ontology.schema.json`. |

This repository holds the corpus source. The generator, validators, and canonical
`ontology.schema.json` live in the `modeled-information-format/MIF` spec repo, not
here.

## Related

- [Ontology model](https://modeled-information-format.github.io/ontologies/explanation/ontology-model/)
- [Add a domain ontology](https://modeled-information-format.github.io/ontologies/how-to/add-a-domain-ontology/)
