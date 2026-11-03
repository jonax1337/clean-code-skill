import assert from "node:assert/strict";
import { test } from "node:test";
import { BILLING, CRM, invoice, runCli, writeDataDirectory } from "./hidden_support.js";

test("the error for an unknown customer names the customer id and is not a raw TypeError", () => {
  const invoices = [invoice("H-01", "C-2001", "2026-09-01", [1, 1000]), invoice("H-02", "C-9999", "2026-09-02", [1, 2000])];
  const result = runCli(writeDataDirectory({ billing: BILLING, crm: CRM, invoices }));
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /C-9999/);
  // The CLI prints "error: <message>" only for an UnknownReferenceError; anything else ends as a stack trace.
  assert.match(result.stderr, /^error: Unknown customer/m);
  assert.doesNotMatch(result.stderr, /Cannot read properties/);
});
