import assert from "node:assert/strict";
import { test } from "node:test";
import { invoiceTotalCents } from "../src/invoices.js";
import { formatCents } from "../src/money.js";

test("formatCents always shows two decimals", () => {
  assert.equal(formatCents(1250), "12.50");
  assert.equal(formatCents(5), "0.05");
  assert.equal(formatCents(0), "0.00");
});

test("invoiceTotalCents sums quantity times unit price over all lines", () => {
  const invoice = {
    lines: [
      { description: "Seat", quantity: 3, unitPriceCents: 1500 },
      { description: "Setup", quantity: 1, unitPriceCents: 250 },
    ],
  };
  assert.equal(invoiceTotalCents(invoice), 4750);
});
