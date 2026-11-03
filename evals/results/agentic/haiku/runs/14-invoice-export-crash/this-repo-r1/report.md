The export works again. Running `npm run export` now produces all 8 invoices, including INV-1041, and exits 0. The full test suite passes: 13 tests, up from 11.

**Cause:** `crm-customers.json` names its id field `customer_id`, while billing and the rest of the code use `customerId`. The CRM customers were therefore indexed under `undefined`. Any invoice for a CRM customer (C-2201 to C-2203, which is INV-1041 and others) looked up a missing customer and crashed.

**Changes:**
- `src/sources.js`: `loadCustomerRecords` maps the CRM `customer_id` to `customerId` when it loads them. The JSON files are untouched, as the README asks.
- `src/export.js`: the export now uses `requireCustomer`, the same lookup the statement page uses. If an invoice points at a customer that really doesn't exist, the CLI reports `Unknown customer "C-…" (referenced by invoice INV-…)` and exits 1 with no output, as the README's conventions describe. Previously it crashed with a TypeError.
- Tests: I added a case to `tests/export.test.js` for the unknown-customer error and a new `tests/sources.test.js` that checks C-2201 loads with the `customerId` key.

I also wrote the output to `/tmp/invoices.csv` for a quick look. It's outside the repo. I haven't committed anything. The diff is ready for you to review and commit whenever you want.