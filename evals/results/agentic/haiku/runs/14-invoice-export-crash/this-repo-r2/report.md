The export runs again and the CSV is complete, with all 8 invoices and no crash. The cause was a key-name mismatch in the CRM data.

**Cause:** `data/crm-customers.json` writes the customer id as `customer_id`, while billing and the rest of the code use `customerId`. So the CRM customers, including `C-2201` used by INV-1041, were never indexed. The lookup returned `undefined` and `customer.name` threw.

**Changes:**
- `src/sources.js`: CRM records are translated to `customerId` as they are read. The JSON files are untouched, as the README requires.
- `src/export.js`: the customer lookup now goes through `requireCustomer`, as the README's conventions describe. A customer that really is missing now gives an `UnknownReferenceError` naming the invoice, and the command exits with status 1 and no output, instead of a `TypeError`. The export still never skips a row.
- `tests/sources.test.js` (new): checks that CRM records get `customerId`. It uses a temp directory, not the real data.
- `tests/export.test.js`: added a test for an invoice with an unknown customer.

**Verification:**
- `npm test`: 13 pass, 0 fail (was 11 before, plus the 2 new tests).
- `npm run export`: exit 0, 8 rows. INV-1041 is `Birch & Co,2026-10-11,120.00`, which matches 8 × 1500 cents.

I did not run the new tests against the old code to confirm they fail there. By reading the code, the sources test would get `undefined` for `customerId`, and the export test would get a `TypeError` rather than `UnknownReferenceError`.

I have not committed anything. The fix is in the working tree for you to review.