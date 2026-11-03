The export works again. `npm run export` now writes all 8 invoices, including INV-1041, and the test suite passes (13/13).

**Cause:** `data/crm-customers.json` spells the id field `customer_id`, while the code and the billing file use `customerId`. The customer index was keyed on `customerId`, so every CRM customer was stored under `undefined`. INV-1041 belongs to `C-2201` (Birch & Co, a CRM customer), so the lookup returned `undefined` and `customer.name` threw.

**Fix:** In `src/sources.js`, `loadCustomerRecords` now renames `customer_id` to `customerId` for CRM records as they are loaded. I didn't touch the data file or the CSV format, and I didn't skip or placeholder any invoices.

**Test:** I added `tests/sources.test.js`, which checks that CRM customers resolve by `customerId` and that the normalized records no longer carry `customer_id`.

Nothing is committed yet. The changes are `src/sources.js` (modified) and `tests/sources.test.js` (new). Tell me if you want a commit.

**Not changed:** `src/export.js` still does a direct `customers.get(...).name` lookup. If an invoice ever points at a customer that really doesn't exist in either system, you'll still get the raw `TypeError`, not the `UnknownReferenceError` message the README describes. Switching that lookup to `requireCustomer` is a small change that would give a clear error. I left it out to keep this fix narrow, but I can make it if you want.