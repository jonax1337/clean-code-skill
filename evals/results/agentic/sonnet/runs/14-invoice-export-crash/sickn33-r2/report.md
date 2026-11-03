`npm run export` now runs to the end and writes all 8 invoices. INV-1041 comes out as `Birch & Co`. All 13 tests pass, including the new ones. I haven't committed anything.

**Cause:** the billing file names the id field `customerId`, but `crm-customers.json` uses `customer_id`. Every CRM customer (the `C-22xx` ids) was therefore indexed under `undefined`. Invoices for those customers found no match, and `customer.name` crashed. INV-1041 belongs to `C-2201`, which is a CRM customer.

**Changes:**
- **`src/sources.js`:** CRM records are renamed from `customer_id` to `customerId` when loaded. The CSV format is unchanged.
- **`src/export.js`:** the customer lookup now uses `requireCustomer`. An invoice whose customer really doesn't exist now fails with `Unknown customer "C-9" (referenced by invoice INV-x)` and exit status 1. Before, it crashed with the `TypeError`. This follows the README rule that the export never skips a record.
- **Tests:** I added one test that CRM customers are indexed by `customerId` (`tests/sources.test.js`) and one for the unknown-customer error in the export (`tests/export.test.js`).

You can generate the file with `npm run export > invoices.csv`.