The export now runs end to end and writes all 8 invoices, including INV-1041 (Birch & Co). The 12 tests pass.

**Cause:** the customers come from two systems that name the ID field differently. Billing uses `customerId`, but the CRM file uses `customer_id`. `buildCustomerIndex` only read `customerId`, so every CRM customer (C-2201, C-2202, C-2203) was indexed under `undefined`. Any invoice for one of them then found no customer and crashed. That's why only some invoices failed.

**Changes:**
- **`src/customers.js`:** `buildCustomerIndex` accepts either key and normalizes it to `customerId`. I left the input files alone, since the README says they're read as delivered.
- **`src/export.js`:** the export now looks customers up with `requireCustomer`. A genuinely unknown customer gives `Unknown customer "X" (referenced by invoice INV-…)` and exit status 1 with no output. That follows the README rule that the export never skips a record or prints a placeholder. Before, it was a bare `TypeError`.
- **`tests/customers.test.js`:** I added a test for CRM-style records. I also changed three existing assertions from `equal` to `deepEqual`, because the index now stores a normalized copy of each record.

Nothing is committed. Run `npm run export > invoices.csv` to produce the file for accounting.