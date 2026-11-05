The export works again. `npm run export` now writes all 8 invoices, INV-1041 included, and exits with status 0.

**Cause:** the two customer files use different names for the ID field. `billing-customers.json` calls it `customerId`, but `crm-customers.json` calls it `customer_id`. The loader read both files as delivered, so none of the CRM customers (C-2201, C-2202, C-2203) could be found by ID. That's why it failed only on some invoices: INV-1041 (Birch & Co), INV-1043 and INV-1045. Billing customers were fine.

**Fix (two small changes):**
- `src/sources.js`: when the CRM file is loaded, its records are converted to the billing format. The data files are left untouched, and the CSV columns don't change.
- `src/export.js`: the export now looks up customers through `requireCustomer`, like the rest of the code does. If an invoice ever points to a customer that really doesn't exist, the CLI now shows `Unknown customer "…" (referenced by invoice …)` and exits with status 1 without writing a partial file. That's the behaviour the README asks for, instead of a raw `TypeError`.

**Tests:** I wrote two tests first and checked that both failed before the fix. One covers the CRM field conversion (`tests/sources.test.js`); the other covers the unknown-customer error (`tests/export.test.js`). All 13 tests pass now. I've only checked the output against the sample `data/` folder in the repo. If the real monthly files are elsewhere, run it on those before sending.

Nothing is committed yet; tell me if you want me to commit it.