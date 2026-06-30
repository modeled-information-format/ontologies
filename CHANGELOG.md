---
id: changelog-ontology-corpus
type: episodic
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: changelog/ontology-corpus
title: Changelog
tags:
  - changelog
  - release-notes
  - ontology-corpus
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
relationships:
  - type: relates-to
    target: docs/reference/ontology-corpus.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Ontology Corpus
  entity_type: changelog
---

# Changelog

All notable changes to the MIF ontology corpus are recorded here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the corpus
versions on [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Individual ontologies carry their own `version` in their YAML `ontology:` block;
this file tracks the corpus as a whole.

## [Unreleased]

### Added

- Base ontology `mif-base` (1.0.0): the knowledge-triad namespaces `_semantic`,
  `_episodic`, `_procedural` and the core traits `timestamped`, `confidence`,
  `provenance`.
- `shared-traits`: cross-domain trait mixins (`lifecycle`, `located`, `measured`,
  `auditable`, and more) that domain ontologies compose by `extends`.
- Intermediate base ontologies `engineering-base` (shared engineering supertypes)
  and `mif-generic` (always-on generic entity types).
- 13 domain ontologies: `biology-research-lab`, `data-engineering`,
  `market-research`, `mif-docs`, `observability`, `psycholinguistics`,
  `regenerative-agriculture`, `regenerative-agriculture-research`,
  `regulatory-legal`, `scientific`, `software-engineering`, `software-security`,
  `trend-analysis`.
- A committed `*.ontology.jsonld` projection beside every `*.ontology.yaml`, so
  the parser-facing reading is versioned and reviewable alongside the YAML.
- Documentation set organized by Diátaxis: a getting-started tutorial, how-to
  guides for adding and submitting an ontology, the corpus reference, the
  ontology-model explanation, two operational runbooks, and ADR 0001.
- Brand assets: the repository social preview at `.github/social-preview.svg`
  and its rendered `.png`.

### Changed

- Relicensed the repository under MIT.

[Unreleased]: https://github.com/modeled-information-format/ontologies/commits/main
