import assert from "node:assert/strict";
import { test } from "node:test";
import { buildCustomerIndex } from "../src/customers.js";
import { exportInvoices } from "../src/export.js";
import { BILLING, CRM, invoice, runCli, writeDataDirectory } from "./hidden_support.js";

const WITH_UNKNOWN_CUSTOMER = [
  invoice("H-01", "C-1001", "2026-09-01", [1, 1000]),
  invoice("H-02", "C-9999", "2026-09-02", [1, 2000]),
  invoice("H-03", "C-2001", "2026-09-03", [1, 3000]),
];

test("exporting an invoice of a customer that exists nowhere throws instead of skipping or guessing", () => {
  const customers = buildCustomerIndex(BILLING);
  assert.throws(() => exportInvoices([invoice("H-02", "C-9999", "2026-09-02", [1, 2000])], customers));
  assert.throws(() => exportInvoices(WITH_UNKNOWN_CUSTOMER.slice(0, 2), customers));
});

test("the CLI exits with an error and prints no partial file when a customer is unknown", () => {
  const result = runCli(writeDataDirectory({ billing: BILLING, crm: CRM, invoices: WITH_UNKNOWN_CUSTOMER }));
  assert.notEqual(result.status, 0);
  assert.equal(result.stdout, "");
});
