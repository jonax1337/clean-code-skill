The export works again. `npm run export` now writes all 8 invoices, INV-1041 included (Birch & Co, 120.00), and exits with status 0.

**Cause:** The two customer files name the id field differently. `billing-customers.json` uses `customerId`, but `crm-customers.json` uses `customer_id`. That meant every customer created in the CRM (C-2201, C-2202, C-2203) was stored under an empty id, so invoices for those customers couldn't find a customer name and crashed. That's why only "some customers" failed.

**Fix:**
- `src/sources.js`: when the CRM file is loaded, its `customer_id` field is renamed to `customerId` so it matches the billing file. The data files themselves stay as delivered, as the README requires.
- `src/export.js`: the customer lookup now uses the existing `requireCustomer` check. If an invoice really points to a customer that doesn't exist, you get the error the README describes, for example `error: Unknown customer "C-404" (referenced by invoice INV-9)`, with exit status 1 and no partial file, instead of a crash.

**Tests:** I added a test in `tests/sources.test.js` that checks CRM customers come out with the same field as billing customers, and one in `tests/export.test.js` for an unknown customer. Without the fix, both new tests fail (11 passed, 2 failed). With it, `npm test` shows 13 passed, 0 failed.

I haven't committed anything. The changes are in the working tree for you to review.