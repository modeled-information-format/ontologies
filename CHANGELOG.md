---
id: changelog-ontology-corpus
type: episodic
created: '2026-06-30T12:00:00Z'
modified: '2026-07-06T00:00:00Z'
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

## [0.4.0] - 2026-07-06

### Added

- Curated `negative_examples` for 59 entity types across 8 packs (`data-engineering`
  0.4.0, `engineering-base` 0.2.0, `market-research` 0.4.0, `mif-generic` 1.1.0,
  `observability` 0.4.0, `software-engineering` 0.7.0, `software-security` 0.4.0,
  `trend-analysis` 0.4.0): 234 human-reviewed near-miss phrases sourced from the
  ranked confusion-pair export of a 666-finding reference corpus (mif-rs#34/#35),
  each grounded in real finding content and targeting a specific gold/top1
  confusion pair. Per MIF ADR-020, these are decision-boundary content only, never
  concatenated into a type's positive embedding document. Regenerated the matching
  `.ontology.jsonld` projections and `ontologies/index.json` for the 8 touched
  packs. Closes #39.

## [0.3.0] - 2026-07-04

### Added

- `heliophysics` (0.1.0, `extends: [physical-science-base]`): 10 entity types
  for the space-weather domain — geomagnetic storms, solar flares, coronal
  mass ejections, solar-terrestrial coupling, the Kp/Dst geomagnetic indices,
  GOES X-ray flare flux, geomagnetically induced currents, aurora
  observations, NOAA G/S/R severity-scale alert levels, and monitoring
  platforms (GOES, ACE/DSCOVR, INTERMAGNET). Grounded in PACS 91.25.-r,
  96.50.-e, 96.60.-j, GFZ Potsdam (Kp), WDC Kyoto (Dst), NOAA GOES/SWPC, NERC
  TPL-007-4 / IEEE C57.163-2016, and the OVATION/Aurorasaurus aurora sources.
- `non-ionizing-radiation` (0.1.0, `extends: [physical-science-base,
  clinical-health-base]`): 8 entity types for non-ionizing EMF exposure —
  power-frequency and RF/microwave exposure sources and quantities (including
  specific absorption rate), regulatory exposure limits, IARC
  carcinogenicity-hazard classifications, and clinical/epidemiological
  exposure/health-outcome findings. Grounded in ICNIRP (2010/2020), IEEE
  C95.1-2019, FCC 47 CFR 1.1310, and IARC Monographs Vol. 102 and Vol. 80.

### Fixed

- `heliophysics.ontology.yaml`'s header comment referenced an internal
  authoring context that did not belong in the corpus; replaced with a plain
  statement of the coverage gap the ontology closes. Comment-only fix, no
  schema or entity change. Closes #36.

## [0.2.2] - 2026-07-04

### Added

- `clinical-health-base` (0.1.0) and `physical-science-base` (0.1.0)
  intermediary base layers (both `extends: [research]`): `clinical-record-subject`,
  `clinical-encounter`, `clinical-observation`, and `diagnostic-classification-entry`
  under `clinical-health-base`; `classification-scheme-entry` and
  `physical-quantity` under `physical-science-base`.
- Five domain ontologies extending those bases: `cardiology`, `health`, and
  `fitness` (0.1.0 each, `extends: [clinical-health-base]`); `plasma-physics`
  and `cosmology` (0.1.0 each, `extends: [physical-science-base]`).
- 75 grounded entity types across the five domain packs, sourced from WHO
  ICD-11/ICF, HL7 FHIR, LOINC, SNOMED CT, ACSM, the Compendium of Physical
  Activities, Open mHealth, PACS, IAU, IVOA, and the Unified Astronomy
  Thesaurus.

### Fixed

- Subtype `required`-field substitutability violations pre-dating this
  release in `scientific` (8), `regenerative-agriculture` (3),
  `regenerative-agriculture-research` (4), and `observability` (2): a
  subtype's `required` set now includes every field its parent requires,
  either by renaming a true naming synonym to the parent's field name or by
  adding a genuinely distinct field the child never modeled. Closes #26.
- `health`'s own `observation` entity type collided with
  `research.ontology.yaml`'s own `observation` type once resolved through
  `health`'s extends chain, both projecting to the same global JSON-LD id
  (`mif:entityType/observation`) with incompatible schemas. Renamed to
  `fhir-observation`.
- The `patient` discovery pattern in `health.ontology.yaml` suggested a
  namespace path declared under the wrong cognitive-triad branch
  (`_semantic/health-clinical-record` instead of the actual
  `_episodic/health-clinical-record`), a broken discovery-routing path.

### Changed

- `scientific` (0.2.1 -> 0.3.0), `regenerative-agriculture` (0.2.0 -> 0.3.0),
  `regenerative-agriculture-research` (0.4.0 -> 0.5.0), and `observability`
  (0.1.0 -> 0.2.0) each take a minor version bump for the field renames
  above: breaking for a consumer that re-vendors and still reads the old
  field name, so a patch bump would understate the change.

## [0.2.1] - 2026-06-30

Re-cut of the burned `v0.2.0` tag (the 0.2.0 immutable release was deleted);
no functional changes from 0.2.0. See [0.2.0] below for the full release notes.

## [0.2.0] - 2026-06-30

### Added

- `platform-engineering` (0.1.0) domain ontology (extends `engineering-base`):
  `developer-portal` and `portal-plugin` (both `subtype_of` `component`),
  `software-template`, `golden-path`, and `portal-integration` (whose
  `integration_category` differentiates identity / scm / cloud / observability /
  incident / security / ci-cd / infrastructure / ticketing bindings).
- `agriculture` and `research` base-layer ontologies (ADR-0003): shared
  supertypes for the agricultural and research domain families.
- Machine-readable `index.json` ontology registry for on-demand vendoring.
- Object+SHA vendoring index (ADR-0002): per-ontology `version`, `file`,
  `sha256`, and `extends[]` closure, so consumers can locate, pin-verify, and
  resolve ancestors.
- MIF-baseline governance configs (CODEOWNERS, branch protection, security
  policy).

### Changed

- Documentation site upgraded from Astro 6 / Starlight 0.40 to Astro 7 /
  Starlight 0.41.
- Trivy license scan adopts the centralized org-wide accepted-license policy.

## [0.1.0] - 2026-06-30

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
- Committed `*.ontology.jsonld` projection beside every `*.ontology.yaml`, so
  the parser-facing reading is versioned and reviewable alongside the YAML.
- Documentation set organized by Diátaxis: a getting-started tutorial, how-to
  guides for adding and submitting an ontology, the corpus reference, the
  ontology-model explanation, two operational runbooks, and ADR 0001.
- Astro + Starlight documentation site.
- Brand assets: the repository social preview at `.github/social-preview.svg`
  and its rendered `.png`.

### Changed

- Relicensed the repository under MIT.

[Unreleased]: https://github.com/modeled-information-format/ontologies/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/modeled-information-format/ontologies/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/modeled-information-format/ontologies/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/modeled-information-format/ontologies/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/modeled-information-format/ontologies/releases/tag/v0.1.0
