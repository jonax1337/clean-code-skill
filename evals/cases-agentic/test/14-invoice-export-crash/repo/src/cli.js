import { buildCustomerIndex } from "./customers.js";
import { UnknownReferenceError } from "./errors.js";
import { exportInvoices } from "./export.js";
import { loadCustomerRecords, loadInvoices } from "./sources.js";

const directory = process.argv[2] ?? "data";

try {
  const customers = buildCustomerIndex(loadCustomerRecords(directory));
  process.stdout.write(exportInvoices(loadInvoices(directory), customers));
} catch (error) {
  if (!(error instanceof UnknownReferenceError)) {
    throw error;
  }
  console.error(`error: ${error.message}`);
  process.exitCode = 1;
}
