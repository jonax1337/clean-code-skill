import assert from "node:assert/strict";
import { test } from "node:test";
import { buildCustomerIndex } from "../src/customers.js";
import { UnknownReferenceError } from "../src/errors.js";
import { customerStatement } from "../src/statement.js";

const acme = { customerId: "C-1", name: "Acme", country: "DE" };
const customers = buildCustomerIndex([acme]);

const invoices = [
  { id: "INV-1", customerId: "C-1", issuedOn: "2026-10-01", lines: [{ description: "Seat", quantity: 2, unitPriceCents: 1500 }] },
  { id: "INV-2", customerId: "C-3", issuedOn: "2026-10-02", lines: [{ description: "Seat", quantity: 1, unitPriceCents: 1500 }] },
  { id: "INV-3", customerId: "C-1", issuedOn: "2026-10-03", lines: [{ description: "Setup", quantity: 1, unitPriceCents: 250 }] },
];

test("customerStatement lists the invoices of one customer and their total", () => {
  assert.deepEqual(customerStatement(invoices, customers, "C-1"), {
    customer: acme,
    invoiceIds: ["INV-1", "INV-3"],
    totalCents: 3250,
  });
});

test("customerStatement for an unknown customer is an error, not an empty statement", () => {
  assert.throws(() => customerStatement(invoices, customers, "C-3"), UnknownReferenceError);
});
