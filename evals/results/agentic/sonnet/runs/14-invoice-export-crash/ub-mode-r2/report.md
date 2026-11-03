`npm run export` now works and writes all 8 invoices. INV-1041 comes out as `Birch & Co`. I committed the fix locally as `e8dc54e` and didn't push, since you didn't ask me to.

**Cause:** The two customer files name the ID field differently. Billing uses `customerId`, but the CRM export uses `customer_id`. The CRM customers (C-2201, C-2202, C-2203) were therefore indexed under `undefined`, and any invoice for one of them found no customer. That's why only some customers crashed.

**Changes:**
- **`src/sources.js`:** The CRM records are now converted to `customerId` when they are read.
- **`src/export.js`:** The export now looks customers up with `requireCustomer`, as the README describes. An invoice for a customer that really doesn't exist now stops with `Unknown customer "…" (referenced by INV-…)` and exit status 1, instead of a `TypeError`. The CSV format is unchanged.

**Tests:** I added one for the CRM ID mismatch and one for the unknown-customer error. The CRM test failed before the fix. The full suite passes (13 of 13).

I didn't run the crapper, dryer or mutator tools from the skill. This was a two-line fix.

Run `npm run export > invoices.csv` to produce the file for accounting.