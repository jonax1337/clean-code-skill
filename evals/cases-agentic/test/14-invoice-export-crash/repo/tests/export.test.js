import assert from "node:assert/strict";
import { test } from "node:test";
import { buildCustomerIndex } from "../src/customers.js";
import { exportInvoices } from "../src/export.js";

const customers = buildCustomerIndex([
  { customerId: "C-1", name: "Acme", country: "DE" },
  { customerId: "C-2", name: "Nordwind, Inc.", country: "US" },
]);

const invoices = [
  {
    id: "INV-1",
    customerId: "C-2",
    issuedOn: "2026-10-01",
    lines: [{ description: "Seat", quantity: 2, unitPriceCents: 1500 }],
  },
  {
    id: "INV-2",
    customerId: "C-1",
    issuedOn: "2026-10-02",
    lines: [
      { description: "Seat", quantity: 1, unitPriceCents: 1500 },
      { description: "Setup", quantity: 1, unitPriceCents: 250 },
    ],
  },
];

test("exportInvoices writes the header and one row per invoice in order", () => {
  assert.equal(
    exportInvoices(invoices, customers),
    ["invoice_id,customer,issued_on,total", 'INV-1,"Nordwind, Inc.",2026-10-01,30.00', "INV-2,Acme,2026-10-02,17.50", ""].join("\n"),
  );
});

test("exportInvoices of no invoices is just the header", () => {
  assert.equal(exportInvoices([], customers), "invoice_id,customer,issued_on,total\n");
});
