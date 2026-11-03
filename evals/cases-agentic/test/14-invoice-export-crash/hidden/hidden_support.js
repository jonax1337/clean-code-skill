import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const CLI = fileURLToPath(new URL("../src/cli.js", import.meta.url));

export const HEADER = "invoice_id,customer,issued_on,total\n";

export const BILLING = [
  { customerId: "C-1001", name: "Acme GmbH", country: "DE" },
  { customerId: "C-1002", name: "Nordwind, Inc.", country: "US" },
];

// Customers created in the CRM arrive with a different id field.
export const CRM = [
  { customer_id: "C-2001", name: "Birch & Co", country: "NL" },
  { customer_id: "C-2002", name: "Lindqvist AB", country: "SE" },
  { customer_id: "C-2003", name: "Tulpen BV", country: "NL" },
];

export function invoice(id, customerId, issuedOn, ...lines) {
  return {
    id,
    customerId,
    issuedOn,
    lines: lines.map(([quantity, unitPriceCents]) => ({ description: "Item", quantity, unitPriceCents })),
  };
}

/** Writes the three input files into a fresh directory and returns its path. */
export function writeDataDirectory({ billing, crm, invoices }) {
  const directory = mkdtempSync(join(tmpdir(), "invoice-export-"));
  writeFileSync(join(directory, "billing-customers.json"), JSON.stringify(billing));
  writeFileSync(join(directory, "crm-customers.json"), JSON.stringify(crm));
  writeFileSync(join(directory, "invoices.json"), JSON.stringify(invoices));
  return directory;
}

export function runCli(directory) {
  return spawnSync(process.execPath, [CLI, directory], { encoding: "utf8" });
}
