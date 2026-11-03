import assert from "node:assert/strict";
import { test } from "node:test";
import { buildCustomerIndex, requireCustomer } from "../src/customers.js";
import { UnknownReferenceError } from "../src/errors.js";

const acme = { customerId: "C-1", name: "Acme", country: "DE" };
const nordwind = { customerId: "C-2", name: "Nordwind", country: "US" };
const birch = { customer_id: "C-3", name: "Birch", country: "NL" };

test("buildCustomerIndex finds customers by id", () => {
  const index = buildCustomerIndex([acme, nordwind]);
  assert.equal(index.get("C-1"), acme);
  assert.equal(index.get("C-2"), nordwind);
  assert.equal(index.size, 2);
});

test("buildCustomerIndex finds CRM customers, which carry customer_id, next to billing customers", () => {
  const index = buildCustomerIndex([acme, birch, nordwind]);
  assert.equal(index.get("C-1"), acme);
  assert.equal(index.get("C-2"), nordwind);
  assert.equal(index.get("C-3"), birch);
  assert.equal(index.size, 3);
});

test("requireCustomer returns the customer", () => {
  assert.equal(requireCustomer(buildCustomerIndex([acme]), "C-1"), acme);
});

test("requireCustomer names the unknown customer and who asked for it", () => {
  const index = buildCustomerIndex([acme]);
  assert.throws(
    () => requireCustomer(index, "C-9", "invoice INV-7"),
    (error) =>
      error instanceof UnknownReferenceError &&
      error.message === 'Unknown customer "C-9" (referenced by invoice INV-7)',
  );
});
