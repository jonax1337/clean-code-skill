`npm run export` now runs to the end and prints all eight invoices, including INV-1041 (Birch & Co). All 13 tests pass, including the two new ones. I haven't committed anything.

**Cause:** The CRM export (`crm-customers.json`) calls the id field `customer_id`. The billing export and the rest of the code use `customerId`. Every CRM customer (C-2201, C-2202, C-2203) was therefore indexed under `undefined`. Any invoice for one of them found no customer, which gave the `undefined.name` crash.

**Changes:**
- `src/sources.js`: CRM records are now converted to `customerId` when they're loaded.
- `src/export.js`: a missing customer now goes through `requireCustomer`. It raises the documented `UnknownReferenceError` (e.g. `Unknown customer "C-9" (referenced by invoice INV-9)`) and exits 1 with nothing on stdout. Before, it was a raw `TypeError`. Real missing customers still stop the export, as the README requires.
- Tests: one for loading CRM customers (`tests/sources.test.js`) and one for the unknown-customer error (`tests/export.test.js`).

The CSV columns and format are the same as before. To produce the file for accounting, run `npm run export > invoices.csv`.