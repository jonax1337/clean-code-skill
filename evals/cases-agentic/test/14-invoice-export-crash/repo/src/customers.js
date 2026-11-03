import { UnknownReferenceError } from "./errors.js";

/**
 * @typedef {object} Customer
 * @property {string} customerId
 * @property {string} name
 * @property {string} country
 */

/** Customers by id, for lookups. */
export function buildCustomerIndex(records) {
  const index = new Map();
  for (const record of records) {
    index.set(record.customerId, record);
  }
  return index;
}

/** The customer with this id; `referencedBy` names the record that asked for it, for the error message. */
export function requireCustomer(index, id, referencedBy) {
  const customer = index.get(id);
  if (!customer) {
    throw new UnknownReferenceError("customer", id, referencedBy);
  }
  return customer;
}
