`npm run export` works again: it exits 0 and prints all 8 invoices, including INV-1041 (Birch & Co, 120.00). The fix is uncommitted in the working tree, so you can review it before accaccounting gets the file.

**Cause:** the CRM file `data/crm-customers.json` spells the id field `customer_id`, but the code reads `customerId`. The three CRM customers (C-2201 to C-2203) were therefore never indexed, and the lookup returned `undefined`.

**Changes:**
- `src/sources.js`: the CRM records are renamed from `customer_id` to `customerId` when they are loaded. This is the one place CRM data enters. I left the data file alone, since the README says both files are read as delivered.
- `src/export.js`: the lookup now uses `requireCustomer`, as the README's conventions say. An unknown customer now produces `UnknownReferenceError` naming the invoice and customer, instead of a TypeError.
- Tests: `tests/sources.test.js` is new and covers the CRM rename. `tests/export.test.js` gets a case for an unknown customer. Both new tests failed before the fix. All 13 tests pass now.

I checked the totals by hand against the invoice lines. INV-1041 is 8 × 15.00 = 120.00, and INV-1040 is 3 × 15.00 + 250.00 = 295.00.

I did not commit, since you didn't ask for one. Tell me if you want it committed and pushed.