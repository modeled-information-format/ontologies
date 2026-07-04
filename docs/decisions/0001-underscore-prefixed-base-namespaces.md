---
id: adr-0001-underscore-prefixed-base-namespaces
type: semantic
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: decisions/ontology-corpus
title: Underscore-Prefixed Base-Type Namespaces
tags:
  - adr
  - accepted
  - namespaces
  - conventions
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
relationships:
  - type: relates-to
    target: ../explanation/ontology-model.md
  - type: relates-to
    target: ../reference/ontology-corpus.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Underscore-Prefixed Base-Type Namespaces
  entity_type: decision-record
---

# ADR-0001: Underscore-Prefixed Base-Type Namespaces

## Status

accepted

## Context

### Background and Problem Statement

The Modeled Information Format (MIF) base ontology, `mif-base`, defines three
top-level namespaces for the knowledge triad: declarative knowledge, time-bound
records, and step-by-step processes. Every domain ontology in the corpus inherits
these through `extends:` and then adds its own namespaces for its subject matter,
such as livestock, soil profiles, incidents, and services.

Base-type namespaces and domain namespaces live in **one path space**. A memory
declares where it belongs with a single `namespace:` string such as
`_semantic/decisions` or `_procedural/runbooks`, and that string is the only
locator a parser or a storage layer gets. The triad names (`semantic`, `episodic`,
`procedural`) are also ordinary English words a domain author might reasonably
reach for. Without a marker, a base namespace and a domain namespace that happen to
share a name are indistinguishable, in the path and on the page.

### Current Limitations

Read a bare path segment like `semantic` and nothing in the string says whether it
is the base-type namespace from `mif-base` or a domain namespace some ontology
defined. Telling them apart requires an out-of-band rule: a hardcoded list of
"these names are base" that every parser, validator, and storage layer must carry
and keep in sync. A domain that defines its own `semantic` namespace then collides
with the base one silently, and the collision surfaces only as a misfiled memory.

## Decision Drivers

### Primary Decision Drivers

- When a parser reads a `namespace:` path, the parser shall determine whether the
  path names a base-type namespace or a domain namespace from the path string
  alone, with no external lookup table.
- If a domain ontology defines a namespace, then that namespace shall not collide
  with a base-type namespace in the shared path space.

### Secondary Decision Drivers

- When a person reads a namespace path, the reader shall recognize a base-type
  namespace on sight.
- The base-type namespace identifier shall remain stable across ontology and
  corpus versions, so that stored memory paths do not break.

## Considered Options

### Option 1: No prefix, bare `semantic`

Write the triad as `semantic`, `episodic`, `procedural` with no marker; domains
add bare names beside them.

- **Pro:** The shortest possible path; nothing to carry, nothing to escape; reads
  as plain words.
- **Con:** Base and domain names share one flat token space. The base `semantic`
  and a domain `livestock` are the same *kind* of token, so kind is unreadable from
  the path. A domain that defines `semantic` collides with the base namespace, and
  the clash is silent.

#### Risk Assessment

- *Technical:* High. Collisions between base and domain names are undetectable in
  the path; disambiguation must move out-of-band into a hardcoded base-name list
  every implementation keeps in sync.
- *Schedule:* Cheap to adopt today, expensive later. Renaming the triad after
  memories already store bare paths breaks every stored `namespace:` value.
- *Ecosystem:* Each implementation must encode and maintain the base-name list
  itself; the convention lives in code, not in the data.

### Option 2: Underscore prefix, `_semantic` (chosen)

Reserve a single leading underscore for base-type namespaces: `_semantic`,
`_episodic`, `_procedural`. Domains keep the entire bare space.

- **Pro:** One character marks base-type, and that marker is in the path string
  itself, so a parser and a person read it the same way. Reserving `_` for the base
  triad leaves every bare name available to domains, so the two never collide. The
  identifier is short and stable.
- **Con:** Every implementation must honor the prefix, and every path string
  carries the sigil verbatim, in frontmatter, in storage paths, and in the JSON-LD
  projection.

#### Risk Assessment

- *Technical:* Low. The marker travels in the path, so no out-of-band table is
  needed and no base/domain collision is possible.
- *Schedule:* Low. The prefix is set once in `mif-base` and inherited; there is
  nothing to renegotiate per domain.
- *Ecosystem:* Low. The convention is self-describing, since a reader infers it
  from a single path, and it is documented in the corpus README and reference.

### Option 3: Another sigil or separator, such as `base:semantic`, `@semantic`, or a `base/` segment

Disambiguate with a different sigil (`@semantic`), a scheme prefix
(`base:semantic`), or an extra path segment (`base/semantic`).

- **Pro:** Also separates base-type from domain; a `base/` segment is explicit
  about intent.
- **Con:** MIF memory paths are stored as directories (`_semantic/decisions/`),
  and `:` and `@` are awkward or reserved in path and URI/JSON-LD syntax. An extra
  `base/` segment deepens every path by one level and complicates the children
  already nested under each triad namespace.

#### Risk Assessment

- *Technical:* Medium. `:` and `@` collide with path and URI semantics used by the
  JSON-LD projection; an added segment increases nesting depth everywhere.
- *Schedule:* Comparable to Option 2 to introduce, heavier to live with.
- *Ecosystem:* Heavier syntax for the same disambiguation the underscore already
  provides.

## Decision

Adopt **Option 2**. The three base-type namespaces are underscore-prefixed
(`_semantic`, `_episodic`, `_procedural`), and a leading underscore is reserved for
base-type namespaces across the corpus.

The convention is encoded directly in the `namespaces:` block of
[`mif-base.ontology.yaml`](https://mif-spec.dev/ontologies/mif-base.ontology.yaml), whose path
format documents `_{top-level}/{sub-namespace}` and whose three top-level keys are
exactly `_semantic`, `_episodic`, and `_procedural`. Domain ontologies inherit
these through `extends: [mif-base]` and add their own namespaces without the
underscore, so the path space stays partitioned by the first character.

A memory locates itself with a single `namespace:` value (`_semantic/decisions`,
`_episodic/incidents`, `_procedural/runbooks`), and the underscore is preserved
verbatim in YAML frontmatter and in the JSON-LD projection.

## Consequences

### Positive

- Base-type versus domain is legible in the path string itself; no implementation
  needs an out-of-band list of which bare names are base.
- Reserving `_` leaves the entire bare namespace space to domains, so a domain
  namespace cannot collide with a base-type one.
- The base identifiers are short and stable, so stored memory paths stay valid
  across corpus versions.

### Negative

- Every implementation (parser, storage layer, validator) must honor the leading
  underscore and preserve it exactly.
- Every path string carries the sigil; authors type and read `_semantic` rather
  than `semantic`. The extra character is the cost of the disambiguation.

### Neutral

- The underscore is a corpus convention carried in the `mif-base` `namespaces:`
  keys and the documentation, not a pattern enforced by a JSON Schema gate in this
  repository.
- The base triad is fixed at three namespaces; the convention says nothing about
  how many children each may hold.

## Decision Outcome

The decision meets its drivers. Disambiguation lives in the path string, so a
parser reads base-versus-domain with no external lookup (primary driver one).
Reserving `_` for the base triad keeps domain namespaces out of the base space, so
they cannot collide (primary driver two). A single leading underscore is legible to
a person at a glance (secondary driver one), and pinning the marker in `mif-base`
keeps the identifiers stable across versions (secondary driver two).

The residual cost, the sigil every path carries and every implementation must
honor, is mitigated by stating the convention in one place and inheriting it: it is
encoded in `mif-base.ontology.yaml` and documented in the corpus README and
ontology reference, so implementations read one rule rather than maintaining a
list.

## Related Decisions

None. This is the first recorded decision for the corpus.

## Links

- [`mif-base.ontology.yaml`](https://mif-spec.dev/ontologies/mif-base.ontology.yaml): the
  `namespaces:` block that encodes `_semantic`, `_episodic`, `_procedural`.
- [The MIF ontology model](https://modeled-information-format.github.io/ontologies/explanation/ontology-model/): how the triad and
  inheritance fit together.
- [Ontology corpus reference](https://modeled-information-format.github.io/ontologies/reference/ontology-corpus/): the namespace and
  trait catalog.

## More Information

The convention is auditable in two places that must agree: the three top-level keys
in the `namespaces:` block of `mif-base.ontology.yaml`, and the namespace note in
the corpus reference documentation. Either drifting from the other is the signal
that this decision has been violated.

## Audit

- 2026-06-30: **Compliant.** `mif-base.ontology.yaml` declares the three base-type
  namespaces as `_semantic`, `_episodic`, and `_procedural`; the corpus README
  documents the underscore-prefix convention. The encoded data and the
  documentation agree.
