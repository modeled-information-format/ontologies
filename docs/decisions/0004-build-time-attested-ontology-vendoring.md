---
id: adr-0004-build-time-attested-ontology-vendoring
type: semantic
created: '2026-06-30T22:00:00Z'
modified: '2026-06-30T22:00:00Z'
namespace: decisions/ontology-corpus
title: Build-Time, Attestation-Verified Ontology Vendoring
tags:
  - adr
  - proposed
  - registry
  - vendoring
  - supply-chain
  - deployment
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T22:00:00Z'
relationships:
  - type: relates-to
    target: 0002-object-keyed-hash-pinned-vendoring-index.md
  - type: relates-to
    target: 0003-research-and-agriculture-base-layers.md
  - type: relates-to
    target: ../reference/ontology-corpus.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Build-Time, Attestation-Verified Ontology Vendoring
  entity_type: decision-record
---

# ADR-0004: Build-Time, Attestation-Verified Ontology Vendoring

## Status

proposed

## Context

### Background and Problem Statement

`https://mif-spec.dev/ontologies/*` is served by the `MIF` repo, which is the sole
publisher of the apex domain and the signer of the served catalog. Under ADR-0002
the served catalog is materialized by committing a **vendored snapshot** of this
corpus into `MIF/public/ontologies/` and regenerating `index.json` with
`MIF/scripts/snapshot-ontology-version.py`. That snapshot is refreshed by a human
running the script and committing the result.

This corpus already ships, per release tag, a **signed, SLSA-attested
`tar.gz`**: `release.yml` builds a deterministic `${NAME}-${VERSION}.tar.gz`,
attests build provenance (`attest-build-provenance`), attests a CycloneDX SBOM
(`attest-sbom`), attests the SAST verdict over the release subject, and
**fail-closed verifies (`gh attestation verify`) before a tag-gated publish** —
"an artifact reaches consumers ONLY if it is byte-identical to what was validated
and its attestations re-verify." The attestable per-version artifact is a
capstone of the project.

### Current Limitations

- **Manual hand-off = structural drift.** The served mirror only refreshes when a
  human re-runs the snapshot script and commits it. When the corpus advanced by
  two merged PRs (platform-engineering; a `regenerative-agriculture-research`
  content change), the served `index.json` silently fell behind — 19 vs. 20
  ontologies and a stale `sha256` — while the source index stayed drift-free.
- **The signed tarball is unused by the publisher.** The strongest artifact the
  project produces (attested corpus release) is not what the served surface is
  built from; the served surface is built from a hand-committed copy.
- **No cross-repo freshness path.** Nothing wires an ontologies release to a MIF
  rebuild, so the served surface cannot self-heal.
- **Base/domain ownership is undifferentiated.** The normative floor
  (`mif-base`, `shared-traits`) and open-growth domain ontologies share one
  materialization path, though they have different governance cadence.

## Decision Drivers

### Primary Decision Drivers

- The served surface must **not** depend on a human remembering to re-vendor;
  drift of the kind observed must become structurally impossible.
- Vendoring must be **fail-closed on attestation**: the publisher admits corpus
  bytes only after `gh attestation verify` passes on the signed release artifact.
- Reuse the existing attested-delivery machinery (`release.yml` +
  `gh attestation verify`), not bespoke fetch/verify glue.

### Secondary Decision Drivers

- Keep one `index.json` contract end to end (ADR-0002) — the publisher enriches,
  never recomputes, the attested `{version, file, sha256, extends[]}` core.
- Separate the governed normative floor from the open-growth domain corpus.
- Preserve the single-publisher, single-signer, single-apex-domain invariant.

## Considered Options

### Option 1: Keep committed-snapshot vendoring (status quo)

Continue committing `MIF/public/ontologies/` via `snapshot-ontology-version.py`.
Simple and hermetic, but retains the manual hand-off that just produced silent
drift; the signed tarball remains unused by the publisher.

### Option 2: Build-time fetch + attestation-verify + untar of the signed tarball (chosen)

At MIF deploy, vendor the corpus by **fetching the tag's signed
`${NAME}-${VERSION}.tar.gz`, running `gh attestation verify` fail-closed, and
untarring** into build output (`dist/`, not committed source — the pattern
already used for the versioned schema mirror). The publisher composes the domain
corpus onto MIF's **canonical base**, then recomputes only the *enriched* catalog
(`latest`/`v0` aliases, versioned URLs) while leaving the attested core index
untouched. The build enumerates release tags for the historical version axis;
each version is one immutable, signed tarball. Deploy is triggered by **either an
ontologies release (`repository_dispatch`, carrying the ref) or a MIF change**,
with a **scattered scheduled** deploy as a convergence backstop; on any
verification failure the deploy **keeps the last-good published surface** and
signals, never publishing partial or unverified bytes.

### Option 3: Let the `ontologies` repo self-publish the served path

Rejected: `mif-spec.dev` is a single apex domain served by one Pages site (`MIF`).
Two repos cannot serve subpaths of one apex domain, so the content owner cannot be
the publisher. MIF must remain the assembler/signer.

## Decision

Adopt **Option 2**. Vendoring becomes a build-time **fetch → `gh attestation
verify` → untar** of the per-version signed corpus tarball, replacing the
committed snapshot as the materialization mechanism of ADR-0002's index contract.

- **Vendoring unit:** the signed, SLSA-attested `${NAME}-${VERSION}.tar.gz`, with
  the byte-stable `index.json` (from `gen-ontology-index.sh`) **packaged inside**
  it so the manifest is itself under attestation. The publisher **enriches** the
  verified index (aliases, versioned URLs); it never recomputes the attested
  `{version, file, sha256, extends[]}` core.
- **Base/domain split:** the normative floor (`mif-base`, `shared-traits`) is
  **canonical in `MIF`** — authored and attested in its own tree, trusted by
  authorship. Domain ontologies grow freely in this repo and are the fetched,
  fail-closed-verified layers. The tarball declares the `mif-base` version it was
  validated against; MIF refuses to compose it onto an incompatible base
  (fail-closed compatibility, not just integrity).
- **Freshness:** deploy triggers on ontologies release (`repository_dispatch`
  with the ref, authenticated via the ADR-011 app fleet), on MIF's own changes,
  and on a scattered scheduled backstop. Concurrency-grouped so bursts collapse
  to one publish. Verification failure ⇒ keep-last-good + signal.
- **No committed mirror:** `public/ontologies/` becomes build output under
  `dist/`; the hand-run snapshot commit is retired.

## Consequences

### Positive

- The observed drift becomes structurally impossible: the release event drives the
  refresh and the schedule guarantees convergence.
- The publisher's trust root is the project's strongest artifact — the served
  surface is exactly the attested tarball's verified bytes, enriched.
- Vendoring reuses `release.yml` + `gh attestation verify` verbatim; no new
  fetch/verify code to maintain.
- Governance matches physics: MIF owns and signs a small, slow normative floor;
  the domain corpus grows open and additive without touching the core.

### Negative

- MIF's Pages build becomes **non-hermetic** (build-time network fetch); mitigated
  by pinning to the dispatched ref and sha/attestation verification.
- The `extends` graph now **crosses repos**: this repo's validators must resolve
  `mif-base` from a pinned, verified MIF version, and a `mif-base` change in MIF
  must run this corpus's validators before merge (reverse validation).
- Cutover must land as one move — MIF fetch/verify/untar deploy, the
  `repository_dispatch` wiring, and retirement of the committed snapshot — or the
  served surface breaks between states.

### Neutral

- The `index.json` contract (ADR-0002) is unchanged; only *who materializes it and
  when* changes. Discovery fields and per-ontology `version` semantics are as-is.
- `engineering-base` and `research` remain domain-side family bases, not part of
  the canonical floor.

## Decision Outcome

The decision meets its drivers: the served surface no longer depends on a manual
snapshot (primary driver one); admission is fail-closed on `gh attestation verify`
over the signed tarball (primary driver two); and it reuses the existing attested
release chain rather than new glue (primary driver three). One index contract is
preserved by enriching, not recomputing, the attested core (secondary driver one),
and the base/domain split gives the normative floor its own governance while
domains grow freely (secondary driver two), all under the single-publisher
invariant (secondary driver three).

The residual costs — a non-hermetic build and a cross-repo `extends` seam — are
accepted: both reduce to "pin the other repo at a verified ref," and the
correctness gate (keep-last-good on verify failure) means freshness is best-effort
*under* integrity, never at its expense.

## Related Decisions

- [ADR-0002: Object-Keyed, Hash-Pinned Ontology Vendoring Index](0002-object-keyed-hash-pinned-vendoring-index.md)
  — the index contract whose **materialization mechanism** this decision replaces
  (committed snapshot → build-time verified vendoring). ADR-0002's shape stands;
  its `snapshot-ontology-version.py` commit step is superseded here.
- [ADR-0003: Research and Agriculture Base Layers](0003-research-and-agriculture-base-layers.md)
  — the domain-side family bases that remain in this repo under the base/domain
  split.
- `research-harness-template` ADR-0012 (on-demand vendoring) — the consumer whose
  fail-closed fetch this pipeline keeps satisfiable.
- **MIF-side companion (to author):** "Deploy assembles a verified external corpus"
  — the publisher-side decision recording the fetch/verify/untar deploy job,
  the `repository_dispatch` contract, and the canonical base ownership.

## Links

- `modeled-information-format/ontologies` `.github/workflows/release.yml`: the
  build → attest → fail-closed-verify → tag-gated-publish chain producing the
  signed `${NAME}-${VERSION}.tar.gz` this decision vendors.
- `scripts/gen-ontology-index.sh`: emits the byte-stable `index.json` packaged
  inside the attested tarball.
- `modeled-information-format/MIF` `scripts/snapshot-ontology-version.py`: the
  committed-snapshot generator whose commit step this decision retires in favor of
  build-time verified vendoring.

## More Information

The invariant to audit: the bytes served at `mif-spec.dev/ontologies/*` must be
the verified contents of a specific signed release tarball, enriched but not
recomputed. If the served core `{version, file, sha256, extends[]}` for any
ontology differs from the attested tarball's `index.json`, this decision has been
violated.

## Audit

- 2026-06-30: **Proposed.** Captures the design agreed in ideation. The MIF deploy
  still reads the committed `public/ontologies/` snapshot; the fetch/verify/untar
  job, the `repository_dispatch` wiring, the base/domain split, and the MIF-side
  companion ADR are not yet implemented.
