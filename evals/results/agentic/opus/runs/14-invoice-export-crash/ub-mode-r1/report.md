The export works again: `npm run export` writes all 8 invoices and exits 0, and INV-1041 now shows Birch & Co.

**Cause:** Customers come from two files. The billing file names the ID field `customerId`, but the CRM file names it `customer_id`. The code only looked for `customerId`, so none of the CRM customers (C-2201, C-2202, C-2203) could be found. That's why only some invoices crashed: INV-1041, INV-1043 and INV-1045.

**Fix (2 commits on `main`):**
1. `ff68558`: when `src/sources.js` reads the CRM file, it now renames that field so CRM customers look the same as billing ones. Nothing after that point needs to know about the difference.
2. `e6ac285`: `src/export.js` now uses the existing `requireCustomer` check. If an invoice points to a customer that really doesn't exist, the CLI now behaves as the README says: it prints something like `error: Unknown customer "C-404" (referenced by invoice INV-9)`, exits with status 1, and writes no file. Before, it crashed with a TypeError. It still never skips an invoice.

**Testing:** I wrote a test for each fix first and watched both fail for the expected reason: the test for 1 got back the CRM field still named `customer_id`, and the test for 2 hit the same TypeError. After the changes, all 13 tests pass.

**Log:**
- Read the code and data and found the field-name mismatch → fixed it where the data is read, not by adding a guard in the export.
- Added `tests/sources.test.js` and an unknown-customer test in `tests/export.test.js` → saw both fail → made the changes → all tests pass, and the real export output looks right.
- Committed in two small commits, each explaining why, what changed and how it was tested.
- Not done: the skill's crapper, dryer and mutator tools aren't in the skill folder (it only has `SKILL.md`), so I couldn't run them.

I haven't pushed yet. Do you want me to push `main`?