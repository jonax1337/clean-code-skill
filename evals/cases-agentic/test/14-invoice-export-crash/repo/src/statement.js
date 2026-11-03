import { requireCustomer } from "./customers.js";
import { invoiceTotalCents } from "./invoices.js";

/** The invoices of one customer with their total, for the customer statement page. */
export function customerStatement(invoices, customers, customerId) {
  const customer = requireCustomer(customers, customerId);
  const own = invoices.filter((invoice) => invoice.customerId === customerId);
  return {
    customer,
    invoiceIds: own.map((invoice) => invoice.id),
    totalCents: own.reduce((sum, invoice) => sum + invoiceTotalCents(invoice), 0),
  };
}
