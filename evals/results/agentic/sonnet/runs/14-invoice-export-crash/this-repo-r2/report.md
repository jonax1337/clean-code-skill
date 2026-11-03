`npm run export` now runs to the end and writes all 8 invoices. INV-1041 comes out as `Birch & Co`, 120.00. `npm test` passes (13 tests), and I haven't committed anything.

**Cause:** `data/crm-customers.json` names the id field `customer_id`, but the billing file and the rest of the code use `customerId`. Every CRM customer (C-2201, C-2202, C-2203) was therefore missing from the lookup, and the export crashed on the first invoice for one of them. That is why only some customers failed.

**Changes:**
- `src/sources.js`: CRM records are renamed to `customerId` when they are loaded. Only the field name changes.
- `src/export.js`: a missing customer now goes through `requireCustomer`. A customer that truly doesn't exist now stops the export with `Unknown customer "C-9" (referenced by invoice INV-9)` and exit code 1, instead of a `TypeError`. That is the behaviour the README describes.
- Tests: `tests/sources.test.js` is new and checks that CRM customers load under `customerId`. `tests/export.test.js` has a new case for an invoice whose customer doesn't exist.

I didn't run the new tests against the old code to confirm they fail there.

The CSV columns and format are unchanged. I only checked the output for the 8 invoices in `data/`, so look over the accounting file before you send it.