The export runs again: all 8 invoices, including INV-1041 (Birch & Co, 120.00). The test suite passes, 14 of 14.

**Cause:** `data/crm-customers.json` names the id field `customer_id`, but the code reads `customerId`. Every CRM customer was indexed under `undefined`, so any invoice for a CRM customer (C-2201, C-2202, C-2203) got `undefined` back and crashed on `.name`.

**Changes:**
- `src/sources.js`: CRM records are renamed from `customer_id` to `customerId` when loaded. The data files are untouched, and the CSV format is unchanged.
- `src/export.js`: the lookup now uses `requireCustomer`, as the README's conventions describe. An invoice with an unknown customer now fails with `Unknown customer "C-x" (referenced by invoice INV-n)` and exit 1, instead of a `TypeError`. It never writes a partial file.
- Tests: `tests/sources.test.js` covers the rename and checks that all CRM customers resolve against the real data. `tests/export.test.js` covers the unknown-customer error.

I haven't committed anything. The `customerStatement` path in `src/statement.js` uses the same index, so it should now also find CRM customers.