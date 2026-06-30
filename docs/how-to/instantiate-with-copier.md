---
id: how-to-instantiate-with-copier
type: procedural
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: how-to/attested-pipeline
title: Instantiate This Template with Copier
tags:
  - how-to
  - attested-delivery
  - copier
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
provenance:
  '@type': Provenance
  sourceType: external_import
  trustLevel: verified
  wasDerivedFrom:
    '@id': https://github.com/attested-delivery
    '@type': prov:Entity
citations:
  - '@type': Citation
    citationType: specification
    citationRole: source
    title: Attested Delivery — the attested release architecture
    url: https://github.com/attested-delivery
relationships:
  - type: relates-to
    target: ../explanation/attested-pipeline.md
  - type: relates-to
    target: ../reference/gates.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Instantiate This Template with Copier
  entity_type: how-to-guide
---

# Instantiate this template with Copier

attested-pipeline-template is a **living, update-propagating template**. You can
stand up a project three ways; they differ in one decisive way — whether you can
later pull template improvements with `copier update`.

| Path | Gets the files | `copier update` later? |
| --- | --- | --- |
| `copier copy` (recommended) | yes | **yes** — records `.copier-answers.yml` |
| GitHub "Use this template" | yes | no (until you adopt Copier) |
| `git clone` | yes | no |

## Option A — Copier (recommended)

```bash
uvx copier copy gh:modeled-information-format/attested-pipeline-template my-project
# or: pipx install copier && copier copy gh:modeled-information-format/attested-pipeline-template my-project
cd my-project
```

Copier asks for the project name, owner, and description; writes a
`.copier-answers.yml` recording your answers and the template version; and
renders the per-instance record at `docs/instance.md`. Only `*.jinja` files are
rendered (suffix dropped); every other file — the attested pipeline workflows,
the VEX disposition, and the gates — is copied verbatim. `copier.yml` is
excluded from instances.

Finish by updating the self-references in `README.md`, `SECURITY.md`, and the
workflows (see `docs/instance.md`).

## Pull later template improvements

This is the differentiator over snapshot engines. When the template ships a fix
or addition, re-apply it to your project:

```bash
cd my-project
copier update   # re-applies template changes, preserving your answers
```

## Option B — GitHub "Use this template"

Still fully supported. This path does not record Copier answers, so
`copier update` will not work until you adopt Copier (run `copier copy` over the
repo and commit the resulting `.copier-answers.yml`).
