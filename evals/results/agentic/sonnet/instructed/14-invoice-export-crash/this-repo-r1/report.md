`npm run export` now finishes and writes all 8 invoices, including INV-1041, which shows as "Birch & Co". I ran `npm test`: 13 tests pass, 2 of them new, and nothing is committed.

**Cause:** the two customer files name the id field differently. Billing customers use `customerId`, but the CRM export uses `customer_id`. So every CRM customer (C-2201, C-2202, C-2203) was indexed under `undefined`, and any invoice for one of them crashed the export. INV-1041, INV-1043 and INV-1045 were all affected.

**Changes:**
- `src/sources.js`: CRM records are now mapped to `customerId` when they're loaded. The data files themselves are untouched, as the README says they're read as delivered.
- `src/export.js`: the export now looks customers up with `requireCustomer`. A genuinely unknown customer will stop the export with `Unknown customer "C-9" (referenced by invoice INV-9)` instead of a `TypeError`. That matches the README rule that the export never skips or placeholders a record.
- Tests: a new `tests/sources.test.js` covers the CRM id mapping, and `tests/export.test.js` gains a case for the unknown-customer error.

The CSV columns are unchanged, so the accounting import should accept the file as before. I didn't check the totals against anything outside the repo.