`npm run export` now runs to the end and writes all eight invoices (INV-1038 to INV-1045). INV-1041 shows as "Birch & Co". All 13 tests pass, including the two I added. I haven't committed anything.

**Cause:** `crm-customers.json` names the id field `customer_id`, but the billing file and the rest of the code use `customerId`. The customers from the CRM (C-2201, C-2202, C-2203) were therefore never findable by id, and the export crashed on the first invoice belonging to one of them.

**Changes:**
- **`src/sources.js`:** CRM records now have `customer_id` renamed to `customerId` when they're loaded.
- **`src/export.js`:** the export now looks customers up with `requireCustomer`. An invoice for a customer that really doesn't exist now stops the export with the `UnknownReferenceError` that the README describes. The CLI prints that error, exits with status 1 and writes no file, instead of crashing with a TypeError.
- **`tests/sources.test.js`:** new tests for both changes.

The CSV columns and format are unchanged.