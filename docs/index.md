---
title: MIF Ontology Corpus
description: The shared, growing corpus of ontologies for the Modeled Information Format — one model a person and a parser read the same way.
template: splash
hero:
  tagline: One model, read the same by a person and a parser — no translation, no drift.
  actions:
    - text: The ontology model
      link: explanation/ontology-model/
      icon: right-arrow
    - text: Author your first ontology
      link: tutorial/author-your-first-ontology/
      variant: minimal
---

## How the corpus fits together

A domain ontology does not invent its own vocabulary. It `extends` a shared base
and adds only what is its own — the machine-cyan typed base every domain builds
on, the human-amber meaning each domain contributes.

```mermaid
graph LR
  base["mif-base<br/>_semantic · _episodic · _procedural"] --> traits["shared-traits"]
  traits --> eng["engineering-base"]
  traits --> sec["software-security"]
  traits --> sci["scientific"]
  traits --> agri["regenerative-agriculture"]
  eng --> sec
```

Each ontology is one pair of files: the `*.ontology.yaml` a person reads and the
generated `*.ontology.jsonld` a parser resolves. Start with
[the ontology model](explanation/ontology-model/) for the why, then
[author your first ontology](tutorial/author-your-first-ontology/) for the how.
