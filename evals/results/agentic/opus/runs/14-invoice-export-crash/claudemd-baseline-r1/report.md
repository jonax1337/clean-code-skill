The export works again. `npm run export` now finishes and writes all 8 invoices, including INV-1041 (Birch & Co).

**Cause:** the customer list is merged from two files. The billing records call the ID field `customerId`, but the CRM records in `data/crm-customers.json` call it `customer_id`. That meant all three CRM customers were looked up under an empty ID, and their invoices (INV-1041, INV-1043, INV-1045) found no customer and crashed.

**Fix:**
- `src/sources.js`: when the CRM file is loaded, its `customer_id` field is renamed to `customerId`, so both sources look the same.
- `src/export.js`: the export now uses the existing `requireCustomer` check. If an invoice ever points to a customer that really doesn't exist, the CLI prints a clear `Unknown customer "…" (referenced by invoice INV-…)` message instead of the `TypeError`.

**Tests:**
- New `tests/sources.test.js`: checks that a CRM-format customer gets loaded and can be found by ID. With the fix temporarily removed, this test fails.
- New case in `tests/export.test.js`: an invoice with an unknown customer gives the clear error message.
- `npm test`: all 13 tests pass.

I checked that every CRM record uses `customer_id` and that no IDs appear in both files, so this fix covers all the current data. Nothing is committed yet. Tell me if you want me to commit it.