# mif-docs

The documentation ontology consumed by the **mif-docs** Claude Code plugin.

It types every document the suite's genres emit — `decision-record`,
`architecture-document`, `runbook`, `requirements-set`, `feature-specification`,
`enhancement-proposal`, and the rest — and declares the typed relationships
(`realized-by`, `derived-from`, `depends-on`, `supersedes`, `relates-to`) plus
the discovery strategies that let an agent traverse from one MIF document to the
related knowledge it points at.

**Consumed by:** `modeled-information-format/mif-docs`. Each genre's emitted
document references this ontology by `id: mif-docs` (canonical URI
`https://mif-spec.dev/ontologies/mif-docs`). The plugin hydrates this definition
at build/release time and validates that every document's `entity.entity_type`
and `relationships[].type` resolve against it.

**Dependencies:** validates against the canonical MIF ontology schema
(`mif-spec.dev/schema/ontology/ontology.schema.json`); extends `mif-base`.
