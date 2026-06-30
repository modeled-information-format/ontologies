# software-security

A MIF `ontologies` pack for the software-security domain. It mints **exactly 10**
security entity types — `vulnerability`, `weakness`, `control`, `threat-actor`,
`attack-campaign`, `indicator-of-compromise`, `security-policy`,
`security-assessment`, `supply-chain-risk`, and `malware` — each grounded in a
named class from an actively-maintained security vocabulary (MITRE ATT&CK,
CVE/CWE/NVD, NIST SP 800-53 / OSCAL / SP 800-161r1, STIX 2.1, VERIS). It extends
`mif-base` and `shared-traits`.

The 3 **extend** types (`security-threat`, `security-framework`,
`security-incident`) are applied in the `software-engineering` pack, not here;
the `defines` and `realizes` relationships reference them as cross-pack
endpoints that resolve across the registry at concordance time.

**Relationships.** Seven security edges from the relationship inventory are
authored: `attributed_to`, `categorizes`, `exploits`, `indicates`, `mitigates`
(local), plus `defines` and `realizes` (cross-pack). Five inventory rows are
intentionally omitted because they reference round-4 expansion types this pack
does not author (no-padding rule): `documents` (threat-intelligence-report),
`hosts` (security-infrastructure), `mitigates` (attack-mitigation → …), `tracks`
(poam), and `uses` (→ security-tool).

- **[software-security — pack reference](https://modeled-information-format.github.io/research-harness-template/reference/packs/ontologies/#software-security)** — its purpose, constraints, goals,
  and how to enable it.

**Dependencies:** None beyond the core harness engine (`jq`, `python3`, `ajv`).

The pack source lives in this directory. It ships disabled; enable it with
`scripts/pack-toggle.sh software-security on`. See the
[MIF research-harness docs](https://modeled-information-format.github.io/research-harness-template/) for the full pack catalog.
