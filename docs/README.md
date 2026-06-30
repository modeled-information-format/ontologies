---
id: reference-docs-index
type: semantic
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: reference/ontology-corpus
title: Documentation Index
tags:
  - reference
  - index
  - documentation
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
relationships:
  - type: relates-to
    target: reference/ontology-corpus.md
  - type: relates-to
    target: explanation/ontology-model.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Documentation Index
  entity_type: reference-document
---

# MIF ontology corpus, documentation

Documentation for the `modeled-information-format/ontologies` corpus, organized by
[Diátaxis](https://diataxis.fr/) type. The first four sections cover the ontologies
themselves; the last two cover the attested release pipeline that ships them.

---

## Tutorial

Learning-oriented. Start here if you are new to authoring ontologies.

| Tutorial | Summary |
|---|---|
| [Author your first ontology](tutorial/author-your-first-ontology.md) | Write a small domain ontology by hand that extends `mif-base` and `shared-traits`, declares a namespace, and composes inherited traits into one entity type |

## How-to guides

Task-oriented. Follow these to accomplish a specific goal.

| Guide | Summary |
|---|---|
| [Add a domain ontology](how-to/add-a-domain-ontology.md) | Add a new flat `ontologies/<name>.ontology.yaml`, generate its JSON-LD projection, and validate it |
| [Submit an ontology](how-to/submit-an-ontology.md) | The end-to-end contribution path: branch, author, validate, open a PR, pass the gates, and release |
| [Instantiate with Copier](how-to/instantiate-with-copier.md) | Stand up a new project from the underlying template and pull future improvements with `copier update` |

## Reference

Information-oriented. Consult these for exact facts.

| Reference | Summary |
|---|---|
| [Ontology corpus reference](reference/ontology-corpus.md) | The full catalog of ontologies, the namespace triad, the trait catalog, the ontology file schema, and conformance rules |
| [Quality gates and workflows](reference/gates.md) | Every workflow (`ci.yml`, `quality-gates.yml`, `release.yml`, `dast.yml`): jobs, triggers, predicate types, and verification commands |

## Explanation

Understanding-oriented. Read these for the reasoning behind the design.

| Explanation | Summary |
|---|---|
| [The ontology model](explanation/ontology-model.md) | Why the corpus is shared and central, how one model is read by a person and a parser, and the reasoning behind the triad, trait composition, and underscore-prefixed base namespaces |
| [The attested pipeline model](explanation/attested-pipeline.md) | The build, attest, verify, publish invariant and why publication is fail-closed |

## Runbooks

Operational procedures for maintainers.

| Runbook | Summary |
|---|---|
| [Release the corpus](runbooks/release-the-corpus.md) | Cut a versioned, attested release by pushing a SemVer tag through the pipeline |
| [CI or release gate failure](runbooks/ci-gate-failure.md) | Diagnose and clear a red security gate on a pull request or release tag |

## Decisions

| ADR | Summary |
|---|---|
| [ADR 0001: underscore-prefixed base namespaces](decisions/0001-underscore-prefixed-base-namespaces.md) | Why `_semantic`, `_episodic`, and `_procedural` carry a leading underscore |

---

For consumer-facing verification instructions see [`SECURITY.md`](../SECURITY.md).
For the org-wide attestation architecture and ecosystem concepts see the
[modeled-information-format docs](https://modeled-information-format.github.io/docs/).
