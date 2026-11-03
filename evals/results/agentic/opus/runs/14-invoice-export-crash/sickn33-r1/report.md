I fixed it. `npm run export` now writes all 8 invoices, including INV-1041 (Birch & Co), and all 14 tests pass.

**Cause:** The two customer files use different field names for the ID. `billing-customers.json` uses `customerId`, but `crm-customers.json` uses `customer_id`. That meant none of the CRM customers (C-2201, C-2202, C-2203) were found by ID. The export crashed on the first invoice for one of them.

**Changes:**
- **`src/sources.js`:** the CRM records get their ID field renamed to match billing when they're loaded. The data files are left untouched, since the README says both files are read as delivered.
- **`src/export.js`:** customers are now looked up with the existing `requireCustomer`. If an invoice ever points to a customer that really doesn't exist, the export now stops with a clear message like `Unknown customer "C-404" (referenced by invoice INV-9)` and writes nothing. That follows the project's rule that no file is better than one missing an invoice.
- **Tests:** I added `tests/sources.test.js` for the loading fix and a test in `tests/export.test.js` for the unknown-customer error.

The CSV columns haven't changed, so the accounting import will take the file as before. Nothing is committed yet; tell me if you want me to commit it.