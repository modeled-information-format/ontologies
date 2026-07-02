---
id: runbook-release-the-corpus
type: procedural
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: runbook/ontology-corpus
title: Release the Ontology Corpus
tags:
  - runbook
  - release
  - ops
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
relationships:
  - type: relates-to
    target: ../reference/ontology-corpus.md
  - type: relates-to
    target: ./ci-gate-failure.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: Release the Ontology Corpus
  entity_type: runbook
---

# Release the ontology corpus

Cut a versioned release of the Modeled Information Format (MIF) ontology corpus
through the attested pipeline. A pushed `vX.Y.Z` tag is the only trigger: it
builds a tarball, attests provenance and an SBOM, runs the security gates, and
publishes a GitHub Release **only** if a fail-closed verify step passes first.

This is a maintainer procedure. Work top to bottom; do not skip the pre-flight.

---

## When to release

Cut a release when the corpus has changed in a way consumers depend on:

- a new domain ontology, or a new entity type, trait, or namespace in an existing ontology;
- a changed `extends:` chain, schema, or relationship that alters how a memory resolves;
- a corrected `.ontology.jsonld` projection.

Do not release for docs-only or CI-only changes.

### Pre-conditions

- You can push tags to `modeled-information-format/ontologies`.
- `gh` is authenticated as an org member (not a work account that lacks org access).
- The version follows [SemVer](https://semver.org/): breaking ontology change → major; additive → minor; fix → patch.

---

## Pre-flight checklist

Run every item before tagging. The release pipeline does **not** validate
ontologies: it ships security attestations, so a malformed ontology will release
cleanly. Validation is your job, here, first.

The ontology validators are **not vendored in this repo**. They live in the
sibling `modeled-information-format/MIF` spec repo under `scripts/`, since MIF
owns `ontology.schema.json`. MIF authors no ontology content of its own
(ADR-018) and no longer keeps a committed mirror of this corpus (ADR-019
replaced that with deploy-time vendoring), so its own CI has nothing local to
run these against. This pre-flight checklist is the only place they run
against your actual changes before release — run them from a MIF checkout,
pointed at this repo with `--path`:

1. **Regenerate JSON-LD projections for any changed YAML.** The
   `.ontology.jsonld` files are committed beside their `.ontology.yaml` source;
   they must match.

   `--all --path` regenerates every `*.ontology.jsonld` in the corpus in one
   pass, for release pre-flight. Authoring a single new ontology instead? See
   [Add a domain ontology](../how-to/add-a-domain-ontology.md), which converts
   just that one file.

   ```bash
   # from a modeled-information-format/MIF checkout
   python scripts/yaml2jsonld.py --all --path /path/to/ontologies/ontologies
   ```

   Commit any regenerated `.jsonld`. A drifted projection is a release blocker.

2. **Validate the corpus.** Both must pass:

   ```bash
   # from a modeled-information-format/MIF checkout
   python scripts/validate-ontologies.py --path /path/to/ontologies/ontologies   # schema conformance + subtype_of integrity
   python scripts/validate-namespaces.py --path /path/to/ontologies/ontologies   # declared namespaces resolve
   ```

   (`scripts/test_subtype_of.py`, also in MIF, only exercises the `subtype_of`
   resolver against its own hardcoded fixtures. It is a regression test for
   that logic, not a check of this corpus, and does not take `--path`.)

3. **Bump the version of every ontology you changed.** In each changed
   `<name>.ontology.yaml`, bump the `version:` under its `ontology:` block.
   Unchanged ontologies keep their version.

4. **Update `CHANGELOG.md`** at the repo root: add an entry for `vX.Y.Z` under a
   dated heading, grouped Added / Changed / Fixed. The tag version and the
   changelog heading must match.

5. **Confirm `main` is green.** `ci.yml` and `quality-gates.yml` must be passing
   on the commit you are about to tag.

   ```bash
   gh run list --repo modeled-information-format/ontologies --branch main --limit 5
   ```

Merge all of the above to `main` before tagging. You tag a commit that is
already on `main` and already green.

---

## Cut the release

Tag the green `main` commit with a SemVer tag and push it. The tag, and nothing
else, triggers `release.yml`.

```bash
git checkout main && git pull
git tag v1.0.0          # the version from your CHANGELOG entry, prefixed with v
git push origin v1.0.0
```

The tag must match `v*.*.*`. The pipeline strips the leading `v`, so tag `v1.0.0`
releases version `1.0.0` and produces artifact `ontologies-1.0.0.tar.gz`. A
pre-release tag (e.g. `v1.0.0-rc.1`, any tag containing `-`) is published as a
GitHub pre-release automatically.

> To rehearse without publishing, run `release.yml` via `workflow_dispatch` from
> any branch. It exercises the full build, attest, and verify chain; the
> `publish` job is tag-gated and is skipped on dispatch.

---

## Watch the pipeline

The tag push starts `release.yml`. Watch it to its terminal state:

```bash
gh run watch --repo modeled-information-format/ontologies \
  "$(gh run list --repo modeled-information-format/ontologies \
       --workflow release.yml --limit 1 --json databaseId -q '.[0].databaseId')"
```

The job graph, in dependency order:

| Job | What it does |
|---|---|
| `meta` | Resolves artifact name and version from the tag |
| `build` | Packs the source tarball into `dist/`; attests SLSA build provenance |
| `sbom` | Generates a CycloneDX SBOM and attests it to the artifact |
| `gate-sast` / `attest-sast` | CodeQL verdict, seam-signed onto the artifact digest |
| `gate-sca` / `attest-sca` | OSV dependency verdict, seam-signed |
| `gate-trivy` / `attest-iac-license` | Trivy IaC/license verdict, seam-signed |
| `vex` | OpenVEX disposition from `.vex/openvex.json`, self-signed |
| `verify` | **Fail-closed** `gh attestation verify` of all six predicates |
| `publish` | Creates the GitHub Release with checksums; **tag-gated, runs only after `verify` passes** |
| `notify-mif` | Mints a `pages` App token and fires a `repository_dispatch` (`ontology-corpus-released`) at `modeled-information-format/MIF`, carrying the tag and version; tag-gated, runs only after `publish` succeeds |

`publish` declares `needs: [meta, verify]` and `if: startsWith(github.ref,
'refs/tags/')`. If `verify` fails, `publish` never runs and nothing is released.
A tag publishes nothing unattested.

`notify-mif` is what makes the release show up at `mif-spec.dev/ontologies/`
without a manual step (ADR-019): the dispatch triggers MIF's own
`deploy.yml`, which fetches this release's tarball, fail-closed
`gh attestation verify`s it the same way `verify` above does, and vendors the
corpus into its Pages build. If `notify-mif` fails, the release itself has
already published successfully; MIF's scheduled backstop deploy will pick up
the new tag on its own within 24 hours, or trigger `deploy.yml` manually via
`workflow_dispatch` in the meantime.

---

## Verify the published release

Once `publish` is green, confirm the Release exists and re-verify its
attestations from your workstation: the same check the pipeline runs, run
independently.

```bash
gh release view v1.0.0 --repo modeled-information-format/ontologies
```

You should see the tarball, the SBOM (`ontologies-1.0.0-sbom.cdx.json`), and a
checksums file attached.

Download the artifact and verify its build provenance:

```bash
gh release download v1.0.0 --repo modeled-information-format/ontologies \
  --pattern 'ontologies-1.0.0.tar.gz'

gh attestation verify ontologies-1.0.0.tar.gz \
  --repo modeled-information-format/ontologies
```

A `PASS` for build provenance confirms the bytes you downloaded are the bytes the
pipeline built and attested. For the SBOM and the seam-signed gate verdicts, see
the verification commands in `SECURITY.md` (the seam-signed predicates require
`--signer-workflow`, not `--repo`).

The release is done.

---

## If the release fails

A failed `verify` is the system working: it blocked an unattested artifact from
publishing. Nothing shipped, so there is nothing to roll back at the release.

1. Read the failing job's log to find which gate or verify check failed.
2. Fix the cause on `main` (re-run the [pre-flight](#pre-flight-checklist)).
3. Re-release. Reuse the tag only after deleting it locally and on the remote
   (`git push origin :refs/tags/v1.0.0`), or, preferred, cut the next patch tag
   so the version history stays append-only.

For diagnosing a specific failed gate or verify step, follow
[Recover from a CI gate failure](./ci-gate-failure.md).

If a bad release already published, do not edit it in place: cut a new patch
version that supersedes it, and note the superseded version in `CHANGELOG.md`.

---

## Related

- [The ontology corpus](../reference/ontology-corpus.md): what ships in a release, every ontology, its version, and its contents.
- [Recover from a CI gate failure](./ci-gate-failure.md): diagnose and clear a failing gate or verify step.
