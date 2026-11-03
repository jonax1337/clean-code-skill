`npm run export` now runs to the end and produces the full file. It writes all eight invoices, and INV-1041 shows as Birch & Co. All 12 tests pass.

**Cause:** the CRM customer file (`data/crm-customers.json`) names the id field `customer_id`. The billing file uses `customerId`. Every CRM customer was therefore stored under the key `undefined`, and any invoice for a CRM customer (C-2201, C-2202, C-2203) failed the lookup.

**Changes:**
- **`src/sources.js`:** CRM records are now converted to `customerId` when loaded, so both sources look the same.
- **`src/export.js`:** the export now uses `requireCustomer`, as the statement page already does. An invoice with a genuinely unknown customer now stops with a clear error, e.g. `Unknown customer "C-404" (referenced by INV-9)`, instead of the TypeError.
- **`tests/export.test.js`:** I added a test for that unknown-customer error.

The unknown-customer error stops the whole export on the first bad invoice. I kept that on purpose, so the accounting file is never silently missing rows. If you would rather skip those invoices and report them, that's a small change.

I haven't committed anything.