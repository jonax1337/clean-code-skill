`npm run export` now runs to the end and writes all 8 invoices, including INV-1041 (Birch & Co, 120.00). The existing 11 tests pass. I didn't add a test for the CRM case.

**Cause:** the two customer files name the id field differently. Billing uses `customerId`, but the CRM file uses `customer_id`. Every CRM customer (the `C-22xx` ids) was therefore indexed under `undefined`. The lookup for those customers returned nothing, and `customer.name` crashed. That is why only some customers failed.

**Changes:**
- `src/sources.js`: CRM records are now mapped to `customerId` when loaded, so everything downstream sees one shape. The customer statement page had the same problem and is fixed by this too.
- `src/export.js`: the export now looks customers up with `requireCustomer`. An invoice that points to a customer that really doesn't exist will stop the export with a clear message, such as `Unknown customer "C-9" (referenced by invoice INV-1050)`. It will no longer fail with a `TypeError`.

I haven't committed anything. Please check the totals against what accounting expects before you send the file.