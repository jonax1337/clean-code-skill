The export runs again and all 8 invoices are written, including INV-1041. The test suite passes (12 of 12).

**Cause:** `data/crm-customers.json` names its id field `customer_id`, but the billing file and the code use `customerId`. The loader passed the CRM records through unchanged, so all three CRM customers were indexed under `undefined`. Any invoice for a CRM customer, such as INV-1041 (`C-2201`, Birch & Co), found no customer and crashed on `.name`. Most invoices were fine because they belong to billing customers.

**Changes:**
- `src/sources.js`: the CRM records are now mapped from `customer_id` to `customerId` when loaded. The export format is unchanged.
- `src/export.js`: the lookup now uses `requireCustomer`, as the README's conventions describe. If a customer is ever missing again, the export fails with a message like `Unknown customer "C-9" (referenced by invoice INV-7)` and exits with status 1, instead of a TypeError. It still never skips a row or writes a placeholder.
- `tests/sources.test.js` (new): checks that the CRM customers resolve by id.

I haven't committed anything. The file for accounting is in `npm run export > invoices.csv`. Running that with the current data gives the complete file.