import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import starlightLlmsTxt from "starlight-llms-txt";
import astroMermaid from "astro-mermaid";

// MIF Ontology Corpus documentation site — Astro + Starlight, modeled on the
// org's doc-site (same versions, same llms.txt + Mermaid + mif-brand wiring).
// Deployed to project Pages at /ontologies; the docs/ tree is sourced via the
// src/content/docs symlink (see src/content.config.ts).
export default defineConfig({
  site: "https://modeled-information-format.github.io",
  base: "/ontologies",
  integrations: [
    astroMermaid(),
    starlight({
      plugins: [starlightLlmsTxt()],
      title: "MIF Ontologies",
      customCss: ["./src/styles/mif-brand.css"],
      logo: {
        light: "./src/assets/logo-light.svg",
        dark: "./src/assets/logo-dark.svg",
        replacesTitle: true,
      },
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/modeled-information-format/ontologies",
        },
      ],
      sidebar: [
        { label: "Tutorial", items: [{ autogenerate: { directory: "tutorial" } }] },
        { label: "How-to guides", items: [{ autogenerate: { directory: "how-to" } }] },
        { label: "Reference", items: [{ autogenerate: { directory: "reference" } }] },
        { label: "Explanation", items: [{ autogenerate: { directory: "explanation" } }] },
        { label: "Decisions (ADRs)", items: [{ autogenerate: { directory: "decisions" } }] },
        { label: "Runbooks", items: [{ autogenerate: { directory: "runbooks" } }] },
        {
          label: "MIF ecosystem",
          items: [
            { label: "MIF home", link: "https://modeled-information-format.github.io/" },
            { label: "Ecosystem docs", link: "https://modeled-information-format.github.io/docs/" },
            { label: "Research harness", link: "https://modeled-information-format.github.io/research-harness-template/" },
            { label: "mif-docs plugin", link: "https://modeled-information-format.github.io/mif-docs-plugin/" },
            { label: "Plugin marketplace", link: "https://modeled-information-format.github.io/claude-code-plugins/" },
            { label: "mif-rs", link: "https://modeled-information-format.github.io/mif-rs/" },
            { label: "Structured MADR", link: "https://smadr.dev" },
            { label: "Specification (mif-spec.dev)", link: "https://mif-spec.dev" },
            { label: "Ontology registry (mif-spec.dev)", link: "https://mif-spec.dev/ontologies/" },
          ],
        },
      ],
    }),
  ],
});
