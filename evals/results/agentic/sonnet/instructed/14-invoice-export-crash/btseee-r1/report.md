`npm run export` now runs to the end and writes all 8 invoices. INV-1041 comes out as `Birch & Co`. All 13 tests pass, including two new ones.

**Cause:** The customer data comes from two systems that name the id field differently. Billing uses `customerId`. The CRM uses `customer_id`, which affects C-2201, C-2202 and C-2203. Those CRM customers were indexed under `undefined`, so any invoice for them found no customer and crashed on `customer.name`. The affected invoices are INV-1041, INV-1043 and INV-1045.

**Changes:**
- `src/customers.js`: new `customerFromCrmRecord` maps a CRM record to the billing shape.
- `src/sources.js`: `loadCustomerRecords` applies that mapping to the CRM file as it loads it.
- `src/export.js`: it now uses `requireCustomer`, so a truly unknown customer fails with `Unknown customer "C-9" (referenced by invoice INV-x)` instead of a `TypeError`. That follows the README rule that the export never skips or guesses a record.
- Tests: one covers the CRM mapping and one covers the unknown-customer error.

The CSV columns and format are unchanged, so the accounting import should accept it as before. Run `npm run export > invoices.csv` to produce the file. I haven't done that or committed anything.