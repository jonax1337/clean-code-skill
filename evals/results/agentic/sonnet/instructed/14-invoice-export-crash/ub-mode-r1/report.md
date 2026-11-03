`npm run export` now runs to the end and writes the full CSV, including INV-1041 (Birch & Co). All 12 tests pass.

**Cause:** the CRM customer file (`data/crm-customers.json`) names the id field `customer_id`. The billing file uses `customerId`. The CRM customers were therefore stored under an `undefined` id, and any invoice for one of them (C-2201, C-2202, C-2203) crashed the export. That is why only some customers failed.

**Fix:** `src/sources.js` now renames `customer_id` to `customerId` for CRM records when it loads them. I also added `tests/sources.test.js`. It failed with your error before the fix and passes now.

Nothing is committed yet. Tell me if you want me to commit it.