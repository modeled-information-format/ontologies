---
title: MIF Ontology Corpus
description: The shared, growing corpus of ontologies for the Modeled Information Format — one model a person and a parser read the same way.
template: splash
hero:
  tagline: One model, read the same by a person and a parser — no translation, no drift.
  image:
    html: |
      <svg viewBox="0 0 560 440" width="560" height="440" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="MIF Ontology Corpus — a machine-cyan typed base that domain ontologies extend, fanning out as human-amber nodes; the corpus still growing.">
        <title>A shared base, extended by domains</title>
        <desc>The knowledge triad and shared-traits mixins form a typed cyan base; domain ontologies extend it, fanning out to the right as amber nodes — software-security, scientific, regenerative-agriculture, and more — with a dashed node still forming.</desc>
        <defs>
          <linearGradient id="mif-field" x1="0" y1="0" x2="560" y2="440" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#0A0D13"/>
            <stop offset="1" stop-color="#0E121B"/>
          </linearGradient>
          <radialGradient id="growGlowAmber" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0" stop-color="#F5B642" stop-opacity="0.18"/>
            <stop offset="1" stop-color="#F5B642" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <rect width="560" height="440" rx="20" fill="url(#mif-field)"/>
        <rect x="12" y="12" width="536" height="416" rx="14" fill="none" stroke="#222C3C" stroke-width="1.5"/>

        <g transform="translate(238 30) scale(1.55)" fill="none" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
          <path d="M6 42 L6 6 L24 29" stroke="#34D3E8"/>
          <path d="M24 29 L42 6 L42 42" stroke="#F5B642"/>
          <path d="M24 25.6 L27.4 29 L24 32.4 L20.6 29 Z" fill="#E8EEF6" stroke="none"/>
        </g>
        <text x="356" y="68" font-family="ui-monospace, 'SF Mono', Menlo, monospace" font-size="26" font-weight="700" letter-spacing="0.04em" fill="#E8EEF6">MIF</text>
        <text x="280" y="130" text-anchor="middle" font-family="ui-monospace, 'SF Mono', Menlo, monospace" font-size="12" letter-spacing="0.1em" fill="#7C8AA0">ONE BASE, MANY DOMAINS</text>

        <g transform="translate(-157.3 86.3) scale(0.511)" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="1040" cy="236" r="78" fill="url(#growGlowAmber)"/>

          <g stroke="#34D3E8" stroke-width="2.5" fill="none" opacity="0.55">
            <path d="M772 340 L1015 212"/>
            <path d="M772 340 L1040 278"/>
            <path d="M772 340 L1050 350"/>
            <path d="M772 340 L1040 422"/>
            <path d="M772 340 L1015 488"/>
          </g>

          <g fill="#0A2630" stroke="#34D3E8" stroke-width="2">
            <rect x="894" y="302" width="11" height="11" rx="2" opacity="0.8"
                  transform="rotate(-15 899 307)"/>
            <rect x="900" y="376" width="11" height="11" rx="2" opacity="0.8"
                  transform="rotate(10 905 381)"/>
          </g>

          <g fill="#34D3E8">
            <rect x="700" y="300" width="9" height="9" rx="1.5" opacity="0.9"/>
            <rect x="700" y="316" width="9" height="9" rx="1.5" opacity="0.7"/>
            <rect x="700" y="332" width="9" height="9" rx="1.5" opacity="0.55"/>
          </g>
          <g stroke="#2E3A4D" stroke-width="1.5">
            <line x1="709" y1="304.5" x2="740" y2="316"/>
            <line x1="709" y1="320.5" x2="740" y2="320"/>
            <line x1="709" y1="336.5" x2="740" y2="324"/>
          </g>
          <rect x="740" y="306" width="22" height="22" rx="3" fill="#0A2630" stroke="#34D3E8" stroke-width="2.5"/>
          <line x1="751" y1="328" x2="751" y2="372" stroke="#34D3E8" stroke-width="2.5" opacity="0.7"/>
          <rect x="740" y="372" width="22" height="22" rx="3" fill="#0A2630" stroke="#34D3E8" stroke-width="2.5"/>

          <circle cx="1040" cy="278" r="9" fill="#F5B642" opacity="0.78"/>
          <circle cx="1050" cy="350" r="9.5" fill="#F5B642"/>
          <circle cx="1040" cy="422" r="9" fill="#F5B642" opacity="0.86"/>
          <circle cx="1015" cy="488" r="8.5" fill="#F5B642" opacity="0.7"/>
          <circle cx="1015" cy="212" r="9" fill="none" stroke="#F5B642" stroke-width="2.5" stroke-dasharray="3 3"/>

          <g font-family="Menlo, 'SF Mono', 'JetBrains Mono', monospace" letter-spacing="0.02em">
            <text x="734" y="296" text-anchor="end" font-size="17" fill="#AEBCCF">mif-base</text>
            <text x="876" y="268" text-anchor="middle" font-size="17" fill="#34D3E8">extends</text>
            <text x="1000" y="200" text-anchor="end" font-size="17" fill="#F5B642">+new</text>
          </g>
        </g>

        <rect x="146" y="362" width="268" height="30" rx="15" fill="#151B27" stroke="#2E3A4D"/>
        <circle cx="168" cy="377" r="4.5" fill="#34D3E8"/>
        <text x="184" y="381" font-family="ui-monospace, 'SF Mono', Menlo, monospace" font-size="12.5" letter-spacing="0.02em" xml:space="preserve"><tspan fill="#34D3E8">typed base</tspan><tspan fill="#AEBCCF">  ·  domains extend it</tspan></text>
      </svg>
  actions:
    - text: The ontology model
      link: explanation/ontology-model/
      icon: right-arrow
    - text: Author your first ontology
      link: tutorial/author-your-first-ontology/
      variant: minimal
    - text: Browse the corpus
      link: reference/ontology-corpus/
      variant: minimal
    - text: Specification (mif-spec.dev)
      link: https://mif-spec.dev
      icon: external
      variant: minimal
    - text: MIF home
      link: https://modeled-information-format.github.io/
      icon: external
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
