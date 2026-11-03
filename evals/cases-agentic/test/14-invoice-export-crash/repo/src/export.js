import { toCsv } from "./csv.js";
import { invoiceTotalCents } from "./invoices.js";
import { formatCents } from "./money.js";

const HEADER = ["invoice_id", "customer", "issued_on", "total"];

function invoiceRow(invoice, customers) {
  const customer = customers.get(invoice.customerId);
  return [invoice.id, customer.name, invoice.issuedOn, formatCents(invoiceTotalCents(invoice))];
}

/** One CSV row per invoice, in the order given, for the accounting import. */
export function exportInvoices(invoices, customers) {
  return toCsv([HEADER, ...invoices.map((invoice) => invoiceRow(invoice, customers))]);
}
