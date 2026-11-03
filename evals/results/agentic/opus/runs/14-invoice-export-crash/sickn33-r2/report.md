I fixed it. `npm run export` now writes all 8 invoices, INV-1041 included, with the columns unchanged, and all 13 tests pass.

**Cause:** the two customer files use different names for the ID field. `crm-customers.json` has `customer_id`, while `billing-customers.json` has `customerId`. So none of the customers created in the CRM (C-2201, C-2202, C-2203) could be found by their ID. The export crashed on the first invoice for one of them, which was INV-1041 (Birch & Co).

**Changes:**
- **`src/sources.js`**: CRM records are now converted to the billing format when they're loaded. I left the data files alone because the README says they're read as delivered.
- **`src/export.js`**: missing customers are now looked up with `requireCustomer`. If an invoice ever points to a customer that really doesn't exist, the export stops with a clear message like `error: Unknown customer "C-404" (referenced by invoice INV-9)` and exit status 1. It no longer crashes with a `TypeError`, which matches what the README says should happen.
- **Tests**: one new test checks that customers from both files load the same way (`tests/sources.test.js`), and one checks the message for an unknown customer (`tests/export.test.js`).

I haven't committed anything. To create tomorrow's file, run `npm run export > invoices.csv`.