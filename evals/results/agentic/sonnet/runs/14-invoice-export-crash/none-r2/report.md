`npm run export` now finishes and writes all 8 invoices, and the 11 existing tests pass. I haven't committed anything.

**Cause:** the billing export names the customer id field `customerId`, but the CRM export names it `customer_id`. The CRM customers (the C-22xx ids, such as INV-1041's C-2201) were therefore indexed under `undefined`. Looking them up by id found nothing, and the missing customer caused the crash on `.name`. Invoices for billing customers (C-100x) worked, which is why only some customers failed.

**Changes:**
- `src/sources.js`: CRM records are renamed to `customerId` when loaded. This is the actual fix.
- `src/export.js`: the export now looks customers up with `requireCustomer`. If an invoice ever points at a customer that doesn't exist, you get `Unknown customer "C-xxxx" (referenced by invoice INV-xxxx)` instead of a TypeError.

INV-1041 now exports as `Birch & Co`. Check the output file before sending it to accounting.

I didn't add a regression test for the CRM id mapping. I can add one if you want.