`npm run export` now finishes and writes all 8 invoices, including INV-1041 (Birch & Co). All 13 tests pass. I haven't committed anything.

**Cause:** the customers come from two systems. The billing export names the id field `customerId`, but the CRM export names it `customer_id`. The lookup is keyed on `customerId`, so every CRM customer ended up under `undefined`. Any invoice for a CRM customer (C-2201, C-2202, C-2203) then found no customer and crashed on `.name`.

**Changes:**
- **`src/sources.js`:** CRM records are now renamed from `customer_id` to `customerId` as they are loaded. The CSV format is unchanged.
- **`src/export.js`:** the export now looks customers up with `requireCustomer`, as `statement.js` does. A truly unknown customer now stops the export with `Unknown customer "C-404" (referenced by INV-9)` and exit status 1. Before, it crashed with an unhelpful `TypeError`. This matches the "no file is better than a wrong file" rule in the README.
- **Tests:** I added `tests/sources.test.js` (CRM customers are found by id) and an unknown-customer case in `tests/export.test.js`. I didn't run either against the old code to watch it fail.

The CSV is ready to generate with `npm run export > invoices.csv`. I haven't checked the totals against anything.