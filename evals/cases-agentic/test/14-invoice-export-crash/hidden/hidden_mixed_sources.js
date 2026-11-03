import assert from "node:assert/strict";
import { test } from "node:test";
import { BILLING, CRM, HEADER, invoice, runCli, writeDataDirectory } from "./hidden_support.js";

const INVOICES = [
  invoice("H-01", "C-2001", "2026-09-01", [2, 1500]),
  invoice("H-02", "C-1001", "2026-09-02", [1, 49900]),
  invoice("H-03", "C-2002", "2026-09-03", [3, 1400], [1, 250]),
  invoice("H-04", "C-1002", "2026-09-04", [5, 100]),
  invoice("H-05", "C-2001", "2026-09-05", [1, 2500]),
  invoice("H-06", "C-2003", "2026-09-06", [10, 1999]),
  invoice("H-07", "C-2002", "2026-09-07", [1, 1]),
  invoice("H-08", "C-1001", "2026-09-08", [2, 1250]),
];

function exportMixed() {
  const result = runCli(writeDataDirectory({ billing: BILLING, crm: CRM, invoices: INVOICES }));
  assert.equal(result.status, 0, result.stderr);
  return result.stdout;
}

test("every invoice gets the name of its own customer, whichever system the customer came from", () => {
  assert.equal(
    exportMixed(),
    HEADER +
      [
        "H-01,Birch & Co,2026-09-01,30.00",
        "H-02,Acme GmbH,2026-09-02,499.00",
        "H-03,Lindqvist AB,2026-09-03,44.50",
        'H-04,"Nordwind, Inc.",2026-09-04,5.00',
        "H-05,Birch & Co,2026-09-05,25.00",
        "H-06,Tulpen BV,2026-09-06,199.90",
        "H-07,Lindqvist AB,2026-09-07,0.01",
        "H-08,Acme GmbH,2026-09-08,25.00",
        "",
      ].join("\n"),
  );
});

test("no invoice is dropped and the order of the input is kept", () => {
  const rows = exportMixed().trimEnd().split("\n").slice(1);
  assert.deepEqual(
    rows.map((row) => row.split(",")[0]),
    INVOICES.map((entry) => entry.id),
  );
});

test("customers that appear in only one system still work when the other system has none", () => {
  const onlyCrm = runCli(writeDataDirectory({ billing: [], crm: CRM, invoices: INVOICES.filter((e) => e.customerId.startsWith("C-2")) }));
  assert.equal(onlyCrm.status, 0, onlyCrm.stderr);
  assert.equal(onlyCrm.stdout.trimEnd().split("\n").length, 1 + 5);
  const onlyBilling = runCli(writeDataDirectory({ billing: BILLING, crm: [], invoices: INVOICES.filter((e) => e.customerId.startsWith("C-1")) }));
  assert.equal(onlyBilling.status, 0, onlyBilling.stderr);
  assert.equal(onlyBilling.stdout.trimEnd().split("\n").length, 1 + 3);
});
