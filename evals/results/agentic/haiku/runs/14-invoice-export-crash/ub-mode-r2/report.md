The export works again. `npm run export` exits 0 and writes all 8 invoices, including INV-1041, to stdout.

**Root cause:** `data/crm-customers.json` names the id field `customer_id`, while billing and the rest of the code use `customerId`. The three CRM customers (C-2201, C-2202, C-2203) were indexed under `undefined`, so their invoices (INV-1041, 1043, 1045) found no customer and `invoiceRow` read `.name` from `undefined`.

**Changes:**
- `src/sources.js`: CRM records are renamed from `customer_id` to `customerId` when they are loaded. This is the one place the two shapes meet. I did not edit the data file, since the README says the customer files are read as delivered.
- `src/export.js`: the lookup now uses `requireCustomer`, as the README's data-error convention requires. A customer that really is missing now fails with `Unknown customer "C-…" (referenced by invoice INV-…)` and exit 1, instead of a `TypeError`.
- `tests/sources.test.js` (new) and `tests/export.test.js`: one test for the CRM rename and one for the unknown-customer error. I ran both before the fix and saw them fail for the reasons above.

**Verification:** `node --test` passes 13 of 13.

**Notes:**
- I have not committed or pushed. Tell me if you want a commit.
- The CRM export is still writing `customer_id`. If it changes again, the same class of crash will come back. Whoever owns that export should know.
- Nothing is skipped or placeholdered. A missing customer still stops the export, by design.