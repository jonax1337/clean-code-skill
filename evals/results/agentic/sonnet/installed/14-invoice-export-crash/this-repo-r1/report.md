The export now runs and writes all 8 invoices, including INV-1041. `npm test` passes (13 tests, 0 failures), and I ran `npm run export` to confirm the output. I haven't committed anything.

**Cause:** `data/crm-customers.json` names the id field `customer_id`, while the billing file and the rest of the code use `customerId`. Every CRM customer (C-2201, C-2202, C-2203) was therefore indexed under `undefined`. Any invoice for one of them found no customer and crashed on `.name`. INV-1041 is a CRM customer, which is why the failures looked selective.

**Changes:**
- `src/sources.js`: CRM records are now renamed from `customer_id` to `customerId` when they are loaded.
- `src/export.js`: it now uses `requireCustomer`, as the README says it should. An invoice with a truly unknown customer now gives `Unknown customer "C-9" (referenced by invoice INV-9)`, exits with status 1 and prints nothing. Before, it crashed with a `TypeError`.
- Tests: I added one for the CRM id mapping (`tests/sources.test.js`) and one for the unknown-customer error in the export (`tests/export.test.js`).

The CSV format and column order are unchanged. I didn't modify the data files.