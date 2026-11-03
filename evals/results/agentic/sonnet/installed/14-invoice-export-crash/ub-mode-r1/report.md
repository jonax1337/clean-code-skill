`npm run export` now finishes and writes all 8 invoices, including INV-1041 (Birch & Co). The 11 existing tests pass. I haven't committed anything.

**Cause:** The CRM customer file uses `customer_id`, but the billing file and the rest of the code use `customerId`. Every CRM customer (C-22xx) was therefore indexed under `undefined`. Invoices for those customers found no match, which gave the `undefined.name` crash.

**Changes:**
- **`src/sources.js`:** CRM records are now renamed to `customerId` when they are loaded. This is the actual fix.
- **`src/export.js`:** The export now looks customers up with `requireCustomer`. If an invoice points to a customer that really doesn't exist, you get a clear error like `Unknown customer "C-9" (referenced by invoice INV-7)` instead of a crash.

I didn't add a test for the CRM field rename. Say so if you want one.