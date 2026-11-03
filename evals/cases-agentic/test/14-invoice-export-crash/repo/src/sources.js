import { readFileSync } from "node:fs";
import { join } from "node:path";

function readJson(directory, file) {
  return JSON.parse(readFileSync(join(directory, file), "utf8"));
}

export function loadInvoices(directory) {
  return readJson(directory, "invoices.json");
}

/** The customers of both systems in one list: billing first, then the CRM. */
export function loadCustomerRecords(directory) {
  return [
    ...readJson(directory, "billing-customers.json"),
    ...readJson(directory, "crm-customers.json"),
  ];
}
