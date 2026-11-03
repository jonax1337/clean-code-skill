`npm run export` now runs to the end and writes all eight invoices, including INV-1041 (Birch & Co). `npm test` passes, 13 of 13. I haven't committed anything.

**Cause:** `data/crm-customers.json` names the id field `customer_id`, but the rest of the code expects `customerId`. Every customer from the CRM (the `C-22xx` ones) was therefore stored under an undefined id. Invoices for them found no customer, and `invoiceRow` crashed reading `.name`. Billing customers (`C-10xx`) were fine, which is why only some customers failed.

**Changes:**
- `src/sources.js`: CRM records are now converted to `customerId` when they are loaded.
- `src/export.js`: the customer lookup now uses `requireCustomer`, as `statement.js` does. An invoice with a truly unknown customer now stops the export with `Unknown customer "C-404" (referenced by invoice INV-9)` and exit status 1, instead of the `TypeError`. The README already describes this behavior.
- Tests: a new `tests/sources.test.js` covers the CRM id mapping, and `tests/export.test.js` gains a case for an unknown customer.

**Check before sending to accounting:** the export still stops at the first invoice with an unknown customer. It didn't hit one in the current data. If two customers shared an id across billing and CRM, the CRM one would silently win. I didn't check for that.