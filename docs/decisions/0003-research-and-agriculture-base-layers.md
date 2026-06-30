---
id: adr-0003-research-and-agriculture-base-layers
type: semantic
created: '2026-06-30T18:00:00Z'
modified: '2026-06-30T18:00:00Z'
namespace: decisions/ontology-corpus
title: Research and Agriculture Base Layers in the Ontology Spine
tags:
  - adr
  - accepted
  - layering
  - extends
  - is-a
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T18:00:00Z'
relationships:
  - type: relates-to
    target: 0001-underscore-prefixed-base-namespaces.md
  - type: relates-to
    target: 0002-object-keyed-hash-pinned-vendoring-index.md
  - type: relates-to
    target: ../reference/ontology-corpus.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Research and Agriculture Base Layers in the Ontology Spine
  entity_type: decision-record
---

# ADR-0003: Research and Agriculture Base Layers in the Ontology Spine

## Status

accepted

## Context

### Background and Problem Statement

The corpus already layers shared supertypes into base ontologies that domain
packs extend: `mif-base` (the cognitive triad) → `mif-generic` (the MIF built-in
entity kinds) → `engineering-base` (shared engineering supertypes: `component`,
`control`, `policy`, `artifact`, `provenance`, …) → leaf engineering packs
(`software-engineering`, `data-engineering`). The leaf packs declare
`subtype_of` against the base supertypes, so a base-typed relationship endpoint
accepts any specialization (ADR-0011 substitutability in the harness).

Two families of packs do **not** yet have their own base layer:

- **Research packs.** `scientific` carries generic research-methodology types
  (`study`, `research-investigation`, `method`, `measurement`, `hypothesis`,
  `dataset`, `research-publication`, `research-funding`, `research-instrument`)
  that are not biology-specific — they are what *any* research-observation pack
  needs. A future `agriculture-research`, `market-research`-as-research, or
  `clinical-research` pack would re-derive them.
- **Agriculture packs.** `regenerative-agriculture` carries generic farm types
  (`farm`, `field`, `soil-profile`, `crop`, `animal`/`herd`, `equipment`,
  `input`, `harvest-record`, `weather-event`) mixed with regen-specific ones
  (`crop-rotation`, `grazing-plan`, `carbon-baseline`, `carbon-credit`).

### Current Limitations

Without these layers the spine is inconsistent and lossy:

- `regenerative-agriculture-research` extends **`engineering-base`** — an
  *engineering* lineage — though it models *agriculture* research. It inherits
  `component`/`control` rather than research or agriculture supertypes. That is
  the wrong parent.
- `scientific` and `regenerative-agriculture` both extend `mif-base` directly, so
  there is no shared research or agriculture supertype to type a cross-pack
  relationship endpoint against, and every new research/agriculture pack
  re-mints the generic core instead of specializing it (violates the
  reuse-before-mint rule ADR-0001/the build-spec set).

## Decision Drivers

### Primary Decision Drivers

- When a new research or agriculture pack is authored, the pack shall specialize
  shared supertypes via `subtype_of` rather than re-mint generic research or farm
  types.
- If a relationship endpoint is typed at a research or agriculture supertype,
  then any pack's specialization of that supertype shall satisfy the endpoint
  (substitutability).
- A research pack shall extend a research lineage and an agriculture pack an
  agriculture lineage; no pack shall inherit a domain it does not belong to
  (no `agriculture-research` under `engineering-base`).

### Secondary Decision Drivers

- The two base layers shall mirror the shape of `engineering-base` (extends
  `[mif-base, shared-traits]`, supertypes under the cognitive-triad namespaces),
  so the spine stays uniform.
- Existing typed findings shall keep resolving across the re-parenting (migration,
  not a break).

## Considered Options

### Option 1: Keep the flat structure (no new base layers)

Leave `scientific`/`regenerative-agriculture` extending `mif-base` and
`regenerative-agriculture-research` under `engineering-base`.

- **Pro:** Zero migration; nothing moves.
- **Con:** The wrong-lineage parent persists; every new research/agriculture pack
  re-mints the generic core; no shared supertype for cross-pack endpoints.

#### Risk Assessment

- *Technical:* Medium — re-minting drift accumulates; substitutability is unavailable.
- *Schedule:* Free now, costlier per future pack.
- *Ecosystem:* The spine stays inconsistent with the engineering lineage.

### Option 2: Introduce `research` and `agriculture` base layers; re-parent (chosen)

Mint two base ontologies, each `extends: [mif-base, shared-traits]`, modeled on
`engineering-base`:

- **`research`** — generic research-methodology supertypes extracted from
  `scientific`'s non-bio core: `research-study`, `research-investigation`,
  `research-method`, `measurement`, `hypothesis`, `dataset`, `research-output`
  (publication), `research-funding`, `research-instrument`, `research-finding`.
- **`agriculture`** — generic farm supertypes extracted from
  `regenerative-agriculture`: `farm`, `field`, `soil`, `crop`, `livestock`,
  `agricultural-input`, `agricultural-equipment`, `harvest-record`,
  `weather-event`.

Re-parent: `scientific` → `extends: [research]`; `regenerative-agriculture` →
`extends: [agriculture]`; `regenerative-agriculture-research` →
`extends: [research, agriculture]` (it is agriculture research). Leaf packs
declare `subtype_of` against the new supertypes; the generic types they
previously minted become specializations.

- **Pro:** Correct lineage; reuse-before-mint for every future research/agriculture
  pack; shared supertypes enable cross-pack substitutable endpoints; the spine is
  uniform with the engineering lineage.
- **Con:** A migration: re-parenting changes `extends` closures and the vendoring
  index `extends` fields, and every affected finding's type must still resolve.
  It also supersedes the just-completed ADR-0002 promotion of `scientific` (its
  `extends` changes), so the registry promotion must be re-run on the layered
  packs before deploy.

#### Risk Assessment

- *Technical:* Medium — supertype extraction + `subtype_of` wiring must validate;
  `resolve-ontology` must still type the corpus.
- *Schedule:* Medium — adds a base-authoring + re-parent + re-promote pass before
  the ADR-0002 deploy.
- *Ecosystem:* Low once landed; the spine becomes consistent and extensible.

### Option 3: Rename `scientific` to `research` (no agriculture layer)

Treat `scientific` itself as the research base; add no agriculture layer.

- **Pro:** Less new content.
- **Con:** `scientific` carries bio-specific types (`sample-organism`,
  `protocol-application`) that do not belong in a generic base; conflates the base
  with one domain; leaves the agriculture lineage unfixed.

#### Risk Assessment

- *Technical:* Medium — a polluted base re-creates the reuse problem one level up.
- *Schedule:* Cheaper, but half the fix.
- *Ecosystem:* Asymmetric (research fixed, agriculture not).

## Decision

Adopt **Option 2**. Mint `research` and `agriculture` base ontologies (each
`extends: [mif-base, shared-traits]`, supertypes under the triad namespaces,
shaped like `engineering-base`). Re-parent `scientific` onto `research`,
`regenerative-agriculture` onto `agriculture`, and
`regenerative-agriculture-research` onto `[research, agriculture]`. Leaf packs
declare `subtype_of` against the new supertypes; the generic types they minted
become specializations.

**Sequencing (load-bearing):** because this changes `scientific`'s (and the
agriculture packs') `extends`, it **supersedes the ADR-0002 promotion of those
packs**. Land this layering — bases + re-parent + re-merge + re-run the registry
promotion + regenerate the object+sha index — **before** the `mif-spec.dev`
deploy, so the deploy publishes the final layered closure once, not twice.

## Consequences

### Positive

- Correct domain lineage; no pack inherits a domain it does not belong to.
- Reuse-before-mint for every future research/agriculture pack.
- Shared supertypes give substitutable cross-pack relationship endpoints.
- The spine is uniform with the engineering lineage.

### Negative

- A real migration: `extends` closures, vendoring-index `extends` fields, and
  finding type-resolution all move; the ADR-0002 promotion must be re-run on the
  re-parented packs before deploy (extra pass, and the Phase-A `scientific`/
  agriculture commits are superseded).
- Two new published base ontologies to maintain and version.

### Neutral

- The new bases follow the existing `engineering-base` shape, so no new
  conventions are introduced.
- Versioning: the re-parented leaf packs take a version bump (their `extends`
  changed); the new bases ship at `0.1.0`.

## Decision Outcome

The decision meets its drivers: new packs specialize shared supertypes
(driver one); base-typed endpoints accept specializations (driver two); research
packs sit under `research` and agriculture packs under `agriculture`, ending the
engineering-lineage miscategorization (driver three). The bases mirror
`engineering-base` (secondary one) and the re-parenting is a migration that keeps
findings resolving (secondary two). The residual cost — a re-promote pass that
supersedes part of the ADR-0002 work — is mitigated by sequencing the layering
before the single `mif-spec.dev` deploy.

## Related Decisions

- [ADR-0001: Underscore-Prefixed Base-Type Namespaces](0001-underscore-prefixed-base-namespaces.md)
- [ADR-0002: Object-Keyed, Hash-Pinned Ontology Vendoring Index](0002-object-keyed-hash-pinned-vendoring-index.md)
  — its promotion of `scientific`/agriculture packs is superseded by this re-parenting and must be re-run before deploy.

## Links

- `ontologies/engineering-base.ontology.yaml`: the base-layer shape this follows.
- `ontologies/scientific.ontology.yaml`, `regenerative-agriculture.ontology.yaml`,
  `regenerative-agriculture-research.ontology.yaml`: the packs re-parented.

## More Information

Auditable in the `extends:` blocks of the affected packs and the new base
ontologies' `entity_types`/`subtype_of` wiring: a research/agriculture pack whose
`extends` does not name its base layer, or a generic type re-minted in a leaf
instead of specialized from the base, signals this decision has been violated.

## Audit

- 2026-06-30: **Pending.** Accepted; bases authored (collision-free abstract supertypes, discovery disabled), scientific/regenerative-agriculture/regenerative-agriculture-research re-parented with subtype_of (all reachable via extends closure), corpus resolves 36/36. Flip to Compliant once deployed + the harness vendors against the live registry. The base layers are not yet authored and the
  packs not yet re-parented. Flip to Compliant once `research` and `agriculture`
  ship, the three packs extend them with `subtype_of` wiring, the corpus still
  resolves, and the registry is re-promoted on the layered closure.
