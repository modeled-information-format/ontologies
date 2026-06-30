---
id: explanation-ontology-model
type: semantic
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: explanation/ontology-corpus
title: The Ontology Model
tags:
  - explanation
  - ontology
  - design-rationale
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
relationships:
  - type: relates-to
    target: ../reference/ontology-corpus.md
  - type: relates-to
    target: ../tutorial/author-your-first-ontology.md
  - type: relates-to
    target: ../decisions/0001-underscore-prefixed-base-namespaces.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: The Ontology Model
  entity_type: explanation
---

# The Ontology Model

A memory is only as useful as the vocabulary it is typed against. Write "this is
a decision, confidence 0.8, from the design review" in one project's private
shape and another project's private shape, and you have two records that mean the
same thing and can agree on nothing. The Modeled Information Format (MIF) ontology
corpus exists to remove that gap: one shared vocabulary, declared in the open, so
a memory typed in one domain stays legible to tools and people working in another.

This page is about the *why* behind the corpus, why it is central rather than
per-project, why the model is written once and read twice, and the reasoning
behind the three choices that shape every ontology in it: the knowledge triad,
trait composition, and the underscore-prefixed base namespaces. For the catalog
of what the corpus currently holds, see the
[ontology corpus reference](../reference/ontology-corpus.md); to add to it, start
with the [tutorial](../tutorial/author-your-first-ontology.md).

## One vocabulary, not many

The tempting shortcut is for each project to invent its own types as it goes. It
is less work on day one, you name a field, you move on, nothing to agree with
anyone about. The cost arrives later and compounds. Two teams independently model
"a thing we decided," give it different field names and different namespace
paths, and now a memory that should be portable is stranded. Nothing typed in one
project can be discovered, validated, or related against another. The vocabulary
fragments exactly where it would have been most valuable: at the seams between
domains.

A central corpus makes the opposite bet. The knowledge triad, the core traits,
the shared cross-domain traits, the relationship types: these are declared once,
in `mif-base` and `shared-traits`, and every domain ontology builds on them. A
`decisions` memory from a software-engineering ontology and a `decisions` memory
from a regenerative-agriculture ontology share the same base type, the same
`confidence` and `provenance` traits, the same `_semantic/decisions` namespace.
They were authored by different people for different work, and they still
interoperate, because they converge on the same vocabulary underneath. The corpus
is the place that convergence happens, not a registry that polices what each
domain may say, but the common ground each domain extends.

That bet has a real cost, and it is worth naming. A shared vocabulary is a
constraint: a domain author cannot model "a decision" however they please; they
inherit `_semantic/decisions` and compose the base traits whether or not they
would have designed them that way. The corpus trades some local freedom for
cross-domain meaning. For memory that is meant to travel, that trade is the whole
point.

## One model, two readers

Each ontology in the corpus is written once and read twice. A person reads the
YAML; a parser reads the JSON-LD projection committed beside it. They are not two
documents kept in sync: they are one model in two renderings, which is the
property the whole format is built to protect.

Here is the `confidence` trait as a person reads it, in
[`mif-base.ontology.yaml`](../../ontologies/mif-base.ontology.yaml):

```yaml
confidence:
  description: "Adds confidence score for freshness and validity tracking"
  fields:
    confidence:
      type: number
      description: "Confidence score (0.0-1.0)"
```

And the same trait as a parser resolves it, in
[`mif-base.ontology.jsonld`](../../ontologies/mif-base.ontology.jsonld):

```json
"confidence": {
  "@id": "mif:trait/confidence",
  "@type": "mif:Trait",
  "name": "confidence",
  "description": "Adds confidence score for freshness and validity tracking",
  "fields": {
    "confidence": {
      "type": "number",
      "description": "Confidence score (0.0-1.0)"
    }
  }
}
```

The YAML carries the meaning a person needs: a named trait, a description, a
field with a type and a range. The JSON-LD carries the structure a machine needs:
a resolvable `@id`, an `@type` that ties the node to the MIF ontology
vocabulary, the same fields under the same names. Neither is a summary of the
other. The description a person reads is the description a parser stores; the
field a person sees is the field a parser validates. There is no second
translation step where the two could drift apart, because the JSON-LD is a
projection of the YAML, not a re-authoring of it.

In this corpus the YAML is the source of record. The `.ontology.jsonld` files are
committed next to it so the machine reading is versioned and reviewable alongside
the human one. The generator that derives the projection, the validators that
check round-trip fidelity, and the canonical
[`ontology.schema.json`](https://mif-spec.dev/schema/ontology/ontology.schema.json)
they validate against live in the sibling MIF spec repository, which mirrors this
corpus and runs that validation in its pipeline. The split matters: the corpus is
where the vocabulary is authored and reviewed; the spec repo is where it is
mechanically checked. What you read here and what a tool resolves are the same
model.

## Three kinds of knowledge

The base ontology divides everything into three top-level namespaces, and the
division is not arbitrary. It follows a long-standing taxonomy of what knowledge
*is*:

- `_semantic`: facts, concepts, and relationships. Declarative knowledge: what
  is true, what something is, why a choice was made. A decision with its
  rationale lives here, under `_semantic/decisions`.
- `_episodic`: events, experiences, and timelines. Time-bound records: what
  happened and when. An outage and its postmortem live here, under
  `_episodic/incidents`.
- `_procedural`: step-by-step processes. How-to knowledge: the sequence you
  follow to get something done. An operational runbook lives here, under
  `_procedural/runbooks`.

Three, and not more, because these are genuinely different kinds of thing, not
three topics. A fact does not expire the way an event recedes into the past; a
procedure is graded by whether its steps work, not by whether it is true. Typing
a memory by which kind of knowledge it is (before typing it by domain) gives
every tool a coarse, reliable handle that holds across every ontology in the
corpus. A query for "recent incidents" means the same thing whether the incidents
are server outages or failed field trials, because both were typed `episodic`
first and domain-specific second. The triad is the shared spine; the domains hang
their own entity types off it.

## Traits compose; they do not descend

The corpus models shared structure with traits: small, named bundles of fields
that an entity type pulls in by reference. `timestamped` adds `created_at` and
`updated_at`. `confidence` adds a score. `provenance` adds `source` and `author`.
These three are the core traits in `mif-base`. The `shared-traits` ontology adds a
broader cross-domain set (`lifecycle`, `auditable`, `located`, `measured`,
`reviewed`, and more), each one a mixin a domain can compose without redefining it.

The deliberate choice here is composition over inheritance. The corpus could have
modeled a deep class hierarchy: a base `Entity` class, an `AuditableEntity`
subclass, a `LocatedAuditableEntity` below that, and so on, each level fixing what
its descendants must be. Deep hierarchies read tidily on a diagram and turn rigid
in practice. A `soil-profile` is `measured` and `located` but not `auditable`; an
audit record is `auditable` and `reviewed` but has no location. Force those into a
single line of descent and you either duplicate traits across branches or invent
awkward intermediate classes that exist only to hold one combination. Traits as
mixins sidestep that entirely: an entity type lists exactly the traits it needs,
in any combination, and the corpus stays flat and recombinable. The cost is that
there is no single class to point at that says "everything an entity is": the
answer is always the specific list of traits it composed. For a vocabulary that
spans thirteen-plus domains and keeps growing, that flexibility is worth more than
the tidy tree.

This is also why **entity types are not inherited**. An ontology declares what it
builds on with `extends`:

```yaml
ontology:
  id: my-domain
  version: "1.0.0"
  extends:
    - mif-base
    - shared-traits
```

What flows down through `extends` is the reusable material: traits, relationship
types, namespaces, and discovery patterns all become available to the child. The
entity types do not. A domain must define its own entity types explicitly,
composing the inherited traits into them:

```yaml
entity_types:
  - name: soil-profile
    base: semantic
    traits:
      - measured      # from shared-traits
      - located       # from shared-traits
      - provenance    # from mif-base
```

The reasoning is that a `soil-profile` is meaningful only inside the
regenerative-agriculture domain; inheriting it into an observability ontology
would be noise. Traits are the genuinely shared currency and flow freely; entity
types are local and stay local. When more than one parent is listed, they are
applied in order (`mif-base` first, then `shared-traits`) and a later entry
overrides an earlier one on conflict, so `shared-traits` can refine what
`mif-base` established. The layering is intentional: `mif-base` carries the triad
and the core traits, `shared-traits` adds the industry-agnostic mixins, and a
domain ontology adds the specifics. Each layer extends the one beneath without
rewriting it.

## Why the base namespaces start with an underscore

The three base namespaces are written `_semantic`, `_episodic`, and
`_procedural`, underscore first. The prefix is a marker. It says "this namespace
is part of the base model, not something a domain invented," and it makes that
distinction visible at a glance in a path and unambiguous to a parser. A domain
adds its own namespaces without a prefix (`livestock`, `entities`, `features`)
and the underscore keeps the base type triad from ever colliding with or being
mistaken for domain vocabulary. The decision and the alternatives weighed are
recorded in
[ADR 0001, Underscore-Prefixed Base Namespaces](../decisions/0001-underscore-prefixed-base-namespaces.md);
this is the short version of why the convention is worth the small ugliness of a
leading underscore.

## The explicitness is the feature

None of this is free. Declaring a model up front (naming the triad, defining the
traits, composing entity types, projecting to JSON-LD) is more work than dumping
loose JSON and moving on. A loose record costs nothing to write and everything to
trust: no one can say what its fields mean, whether two of them are the same
thing, or whether a tool will read it the way a person did. The corpus front-loads
that work so the trust is built in. A memory typed against an ontology in this
corpus can be validated, related, and discovered, and it means the same thing to
the next person and the next parser that reach it. That up-front explicitness is
not overhead the corpus tolerates: it is the thing the corpus is for.

## How this fits the MIF spec

The corpus is the vocabulary; the [MIF specification](https://mif-spec.dev) is the
format that vocabulary plugs into. A MIF memory declares which ontology it
conforms to with an `ontology` reference (`id`, `version`, and an optional `uri`)
and a `namespace` path such as `_semantic/decisions`. That declaration works the
same way in YAML frontmatter and in JSON-LD, the same two readings the ontologies
themselves carry. The schema that defines a valid ontology,
[`ontology.schema.json`](https://mif-spec.dev/schema/ontology/ontology.schema.json),
is published under the canonical `mif-spec.dev` domain and is what the MIF repo
validates this corpus against. The spec says how a memory is shaped and how it
points at its ontology; the corpus says what the ontologies are. Together they
make one model that a person and a parser read the same way, no translation, no
drift.

## Related

- [Ontology corpus reference](../reference/ontology-corpus.md): the catalog of base ontologies, shared traits, and domain ontologies.
- [Author your first ontology](../tutorial/author-your-first-ontology.md): a hands-on path from empty file to a working domain ontology.
- [ADR 0001: Underscore-Prefixed Base Namespaces](../decisions/0001-underscore-prefixed-base-namespaces.md): the decision record behind the namespace convention.
