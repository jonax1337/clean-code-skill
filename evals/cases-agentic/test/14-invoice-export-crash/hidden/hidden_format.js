import assert from "node:assert/strict";
import { test } from "node:test";
import { buildCustomerIndex } from "../src/customers.js";
import { exportInvoices } from "../src/export.js";
import { BILLING, HEADER, invoice, runCli, writeDataDirectory } from "./hidden_support.js";

const INVOICES = [
  invoice("F-01", "C-1002", "2026-08-01", [2, 1500], [1, 5]),
  invoice("F-02", "C-1001", "2026-08-02", [1, 100000]),
];
const EXPECTED = `${HEADER}F-01,"Nordwind, Inc.",2026-08-01,30.05\nF-02,Acme GmbH,2026-08-02,1000.00\n`;

test("the CSV for billing customers keeps its columns, quoting and amounts", () => {
  assert.equal(exportInvoices(INVOICES, buildCustomerIndex(BILLING)), EXPECTED);
});

test("the CLI prints exactly that CSV for billing customers", () => {
  const result = runCli(writeDataDirectory({ billing: BILLING, crm: [], invoices: INVOICES }));
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, EXPECTED);
});
