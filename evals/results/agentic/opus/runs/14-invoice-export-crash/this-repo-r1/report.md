The export works again. `npm run export` now writes all 8 invoices, including INV-1041 (Birch & Co), INV-1043 and INV-1045, and exits with status 0.

**Cause:** the two customer files name the id field differently. `billing-customers.json` uses `customerId`, but `crm-customers.json` uses `customer_id`. Because of that, none of the CRM customers (C-2201, C-2202, C-2203) could be found by their id, and the export crashed on the first invoice that belonged to one of them.

**Changes:**
- `src/sources.js`: CRM records now get their `customer_id` renamed to `customerId` when the file is loaded. I left the data file as it is, because the README says both files are read as they're delivered.
- `src/export.js`: the export now looks customers up with the existing `requireCustomer`. If an invoice points to a customer that really doesn't exist, it now fails the way the README describes: it prints `Unknown customer "C-9" (referenced by invoice INV-9)`, exits with status 1, and writes nothing to the CSV. Before, it crashed with the unclear `TypeError`.

**Tests:** I added `tests/sources.test.js` for the CRM field rename and a test in `tests/export.test.js` for the unknown-customer error. Both failed before the fix. `npm test` now passes all 13 tests (11 before).

I haven't committed anything. Tell me if you'd like a commit or a PR.