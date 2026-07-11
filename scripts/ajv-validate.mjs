#!/usr/bin/env node
// Minimal ajv CLI replacement for CI: validates one JSON document against one
// JSON Schema (draft 2020-12 + formats), exiting non-zero on failure.
//
// Deliberately NOT the `ajv-cli` package: as of ajv-cli@5.0.0 it carries a
// direct, unpatched dependency on fast-json-patch@^2.0.0 (resolves to 2.2.1),
// which has a high-severity prototype-pollution advisory
// (GHSA-8gh8-hqwg-xf34, fixed in 3.1.1) used only by ajv-cli's unrelated
// `migrate` subcommand. This repo's SCA/dependency-review gates are required
// status checks, so pulling that in for the one `validate` command this
// script actually needs isn't worth it -- using the `ajv`/`ajv-formats`
// libraries directly avoids the vulnerable dependency entirely.
//
// Usage: node scripts/ajv-validate.mjs --schema <path> --data <path>

import { readFileSync } from "node:fs";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i]?.replace(/^--/, "");
    args[key] = argv[i + 1];
  }
  return args;
}

const { schema: schemaPath, data: dataPath } = parseArgs(process.argv.slice(2));
if (!schemaPath || !dataPath) {
  console.error("Usage: ajv-validate.mjs --schema <path> --data <path>");
  process.exit(2);
}

const schema = JSON.parse(readFileSync(schemaPath, "utf8"));
const data = JSON.parse(readFileSync(dataPath, "utf8"));

const ajv = new Ajv2020({ strict: false, allErrors: true });
addFormats(ajv);

const validate = ajv.compile(schema);
const valid = validate(data);

if (!valid) {
  for (const err of validate.errors ?? []) {
    console.error(`${err.instancePath || "/"} ${err.message}`);
  }
  process.exit(1);
}

process.exit(0);
