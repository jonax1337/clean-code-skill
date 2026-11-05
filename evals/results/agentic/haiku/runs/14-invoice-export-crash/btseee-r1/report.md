The export runs again and all 8 invoices now come out, including INV-1041 (Birch & Co). The full test suite passes: 13 of 13.

**Cause:** The CRM customer file (`data/crm-customers.json`) names its id field `customer_id`. The billing file and the invoices use `customerId`. `loadCustomerRecords` merged both lists unchanged, so every CRM customer was indexed under `undefined`. Any invoice for a CRM customer (C-2201 to C-2203) then got `undefined` back, and `.name` crashed. Customers from billing were fine, which is why only some invoices failed.

**Fix:** In `src/sources.js`, the CRM records are now translated to `customerId` when they are loaded. Nothing else changed in the export or the index.

**Test:** I added `tests/sources.test.js`. It checks that every invoice in the real data resolves to a customer, and that Birch & Co is found under C-2201. I didn't run it against the old code, but it would have failed there, since the index had an `undefined` key.

**Not changed:** The CLI still only catches `UnknownReferenceError`, so a genuinely unknown customer id would still print a raw stack trace instead of a clean message. That's a separate improvement, and I left it alone for tomorrow's deadline. Nothing is committed; the changes are in the working tree.