import { UnknownReferenceError } from "./errors.js";

/**
 * A customer as delivered by either system: billing records carry `customerId`, CRM records `customer_id`.
 * @typedef {object} Customer
 * @property {string} [customerId]
 * @property {string} [customer_id]
 * @property {string} name
 * @property {string} country
 */

function customerIdOf(record) {
  return record.customerId ?? record.customer_id;
}

/** Customers by id, for lookups. */
export function buildCustomerIndex(records) {
  const index = new Map();
  for (const record of records) {
    index.set(customerIdOf(record), record);
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
