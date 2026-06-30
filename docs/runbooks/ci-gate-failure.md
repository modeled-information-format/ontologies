---
id: runbook-ci-gate-failure
type: procedural
created: '2026-06-30T12:00:00Z'
modified: '2026-06-30T12:00:00Z'
namespace: runbook/ontology-corpus
title: CI or Release Gate Failure
tags:
  - runbook
  - ci
  - security
temporal:
  '@type': TemporalMetadata
  validFrom: '2026-06-30T00:00:00Z'
  recordedAt: '2026-06-30T12:00:00Z'
  ttl: P1Y
relationships:
  - type: relates-to
    target: ./release-the-corpus.md
  - type: relates-to
    target: ../reference/ontology-corpus.md
ontology:
  '@type': OntologyReference
  id: mif-docs
  version: 1.0.0
  uri: https://mif-spec.dev/ontologies/mif-docs
entity:
  name: CI or Release Gate Failure
  entity_type: runbook
---

# CI or release gate failure

A gate just went red on the Modeled Information Format (MIF) ontology corpus. This
runbook takes you from the red check to a fix. The gates here are **supply-chain
security gates**, not ontology validation; this repo runs no ontology validator
(that lives in the sibling `MIF` spec repo). A red gate means a pinning, code,
dependency, IaC, posture, or attestation problem.

Scope: one red gate, one path to green. Set the repo once:

```bash
REPO=modeled-information-format/ontologies
```

## Symptom & where it shows

| You see | Where | What it is |
|---|---|---|
| A red ✗ on a PR or commit | **Checks** tab / `gh pr checks` | A job in `ci.yml`, `quality-gates.yml`, or `release.yml` exited non-zero |
| A new code-scanning alert | **Security** tab → Code scanning | A SARIF gate (`sast`, `sca`, `trivy`, `posture`, DAST) recorded a finding |
| A failed workflow run | **Actions** tab / `gh run view` | The run log, including which job in the `needs:` graph stopped the pipeline |

First triage. Find the failing job and read its log:

```bash
gh pr checks <PR> --repo "$REPO"                    # which check is red
gh run view <run-id> --repo "$REPO" --log-failed    # the failing job's log only
```

For a SARIF gate, list the open alerts instead of scrolling the log:

```bash
gh api "/repos/$REPO/code-scanning/alerts?state=open" \
  --jq '.[] | {tool: .tool.name, rule: .rule.id, sev: .rule.security_severity_level, path: .most_recent_instance.location.path}'
```

Filter by `.tool.name`: `CodeQL`, `OSV-Scanner`, or `Trivy`.

## Triage table

| Gate (job) | Workflow | What red means | First command to inspect |
|---|---|---|---|
| `pin-check` | `ci.yml` | A `uses:` references an action by tag/branch, not a 40-char SHA | `gh run view <run-id> --repo "$REPO" --log-failed` |
| `validate-workflows` | `ci.yml` | `actionlint` found a workflow-YAML error | `gh run view <run-id> --repo "$REPO" --log-failed` |
| `sast` (CodeQL) | `quality-gates.yml`, `gate-sast` in `release.yml` | SAST finding on the workflows/source (`languages: actions`) | Security tab → Code scanning → `tool=CodeQL`; or the `gh api` query above |
| `sca` (OSV-Scanner) | `quality-gates.yml`, `gate-sca` in `release.yml` | A dependency advisory at severity `high` or above | Security tab → `tool=OSV-Scanner` |
| `trivy` (IaC/license) | `quality-gates.yml`, `gate-trivy` in `release.yml` | Trivy filesystem scan flagged IaC misconfig or a license | Security tab → `tool=Trivy` |
| `posture` (Scorecard) | `quality-gates.yml` | OpenSSF Scorecard regressed a repo-posture check (push/schedule only) | Security tab → `tool=Scorecard` |
| `verify` (fail-closed) | `release.yml` and `dast.yml` | An attestation is missing or doesn't bind to the subject digest; **blocks publish** | `gh run view <run-id> --repo "$REPO" --log-failed` |
| `gate-dast` (ZAP) | `dast.yml` (dispatch only) | ZAP scan of a running target; advisory (`fail-action: false`) | `gh run view <run-id> --repo "$REPO" --log-failed` |

## Per-gate remediation

### `pin-check`: unpinned action

The log names the offending `uses:`. Pin it to a full 40-char commit SHA with a
trailing version comment. Resolve the SHA from the action's repo:

```bash
gh api /repos/<owner>/<action-repo>/commits/<tag> --jq '.sha'
```

Then edit the `uses:` line:

```yaml
uses: owner/action@<40-char-sha>   # vX.Y.Z
```

Any new third-party action must also be on the org Actions allow-list
(`repos/.github/README.md`) or the workflow startup-fails. Push the fix; `pin-check`
re-runs on the PR.

### `validate-workflows`: actionlint error

The log points at the file and line. Fix the YAML/expression, push, re-run.

### `sast` (CodeQL) / `sca` (OSV) / `trivy` (IaC/license): SARIF gates

1. Open the alert in the **Security** tab (or the `gh api` query above). Read the
   rule, severity, and file/line.
2. **True positive** → fix the code, dependency, or IaC config in the PR. For
   `sca`, bump the dependency to a fixed version.
3. **No fix available or not exploitable** → record a disposition, do not silently
   suppress:
   - `sca`/`trivy` CVE with no fixed version → add an OpenVEX statement to
     `.vex/openvex.json` (the `vex` job signs it at release time).
   - `sast`/`trivy` false positive → dismiss the alert in the Security tab with a
     written reason, or justify it inline per the rule's convention.
4. Push; the gate re-runs and the alert clears or carries its disposition.

### `posture` (Scorecard)

A repo-level signal, not a per-PR blocker (`publish-results: false`, runs on
push/schedule). A regression usually means branch protection, token permissions,
or a workflow-permission scope changed. These need repo admin to fix; escalate
to a maintainer (below).

### `verify` (fail-closed): attestation/subject mismatch

`verify` fails because an upstream gate it depends on didn't produce its
attestation, or the subject digest it checks no longer matches. It does not have a
fix of its own; **fix the gate that failed first**:

- Read the log for which predicate failed: build provenance, SBOM (`cyclonedx.org/bom`),
  a seam verdict (`sast/v1`, `sca/v1`, `iac-license/v1`), or VEX (`openvex.dev/ns/v0.2.0`).
- Resolve that upstream job (`build`, `sbom`, `attest-sast`, `attest-sca`,
  `attest-iac-license`, or `vex`), then re-run:

```bash
gh run rerun <run-id> --repo "$REPO" --failed
```

A release is published **only** if `verify` is green; a tag publishes nothing
unattested. Never bypass `verify` to ship.

### `gate-dast` (ZAP)

DAST is `workflow_dispatch`-only and advisory: the verdict is signed regardless of
findings, so `gate-dast` does not block on findings. A red `dast.yml` run is almost
always its own `verify` job (missing `dast/v1` attestation) or a target that was not
reachable. Trigger it against a running target:

```bash
gh workflow run dast.yml --repo "$REPO" -f target=https://<your-running-target>
```

`reusable-zap.yml` pulls `zaproxy/action-full-scan`; that one action must be on the
org Actions allow-list or the run startup-fails.

## Re-run after a fix

```bash
gh run rerun <run-id> --repo "$REPO" --failed   # re-run only failed jobs
gh run watch <run-id> --repo "$REPO"            # follow to green
```

## Escalation

Page a corpus maintainer (`modeled-information-format` org owners) when:

- A `posture` regression needs branch-protection, token, or workflow-permission
  changes; these require **org/repo admin** you may not hold.
- A `sast`/`trivy` alert is a true positive in central reusable workflow logic
  (the `.github` repo), not in this repo's thin caller; the fix lands upstream.
- A new third-party action needs an **allow-list** entry (`repos/.github/README.md`).
- `verify` fails with every upstream gate green and digests matching: a seam or
  signing-identity problem in the central `reusable-attest-scan.yml`, which this
  repo cannot fix.

Do not `--no-verify`, dismiss an alert without a written reason, or relax a gate to
get a merge through. A gate exists to fail; route the real fix instead.

## Related

- [Release the corpus](./release-the-corpus.md): cutting a `vX.Y.Z` tag and what the release pipeline does.
- [Ontology corpus reference](../reference/ontology-corpus.md): what the repo ships and how the corpus is structured.
