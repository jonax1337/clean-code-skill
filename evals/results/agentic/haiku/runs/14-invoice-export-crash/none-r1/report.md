The export works again. All 8 invoices now come out, including INV-1041.

**Cause:** The CRM customer file (`data/crm-customers.json`) names its id field `customer_id`, while the billing file and the code use `customerId`. The three CRM customers (C-2201, C-2202, C-2203) were therefore missing from the lookup table. Any invoice for them got `undefined` as its customer, and the `.name` access crashed. That is why only some customers failed.

**Changes (uncommitted, in the working tree):**
- `src/sources.js`: CRM records are mapped from `customer_id` to `customerId` when loaded. I left the data files alone, since the README says both sources are read as delivered.
- `src/export.js`: the export now uses `requireCustomer`, as the README describes. An unknown customer produces `Unknown customer "X" (referenced by invoice INV-n)` and exit status 1, instead of a TypeError. Nothing is written to stdout in that case.
- Tests: added `tests/sources.test.js` for the CRM mapping and one case in `tests/export.test.js` for the unknown-customer error. `npm test` passes, 13 of 13.

**Output check:** I ran `npm run export` and the totals match the invoice lines by hand. For example, INV-1041 is 8 × 15.00 = 120.00 for Birch & Co. I saved the output to `/tmp/invoices.csv` for a quick look. To produce the file for accounting, run `npm run export > invoices.csv` in the repo.

I haven't committed anything. Tell me if you want a commit.