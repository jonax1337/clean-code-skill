I fixed it, and `npm run export` now writes all 8 invoices, including INV-1041 (Birch & Co), INV-1043 (Lindqvist AB) and INV-1045 (Tulpen BV). The CSV format is unchanged and all 13 tests pass.

**Cause:** the two customer files name the ID field differently. `billing-customers.json` uses `customerId`, but `crm-customers.json` uses `customer_id`. Every customer that came from the CRM (the C-22xx IDs) ended up with no usable ID, so looking up their invoices found nothing and the export crashed on `customer.name`.

**Changes:**
- **`src/sources.js`**: when the CRM file is loaded, `customer_id` is renamed to `customerId`. The data files themselves are untouched, since the README says they're read as delivered.
- **`src/export.js`**: customer lookups now use the existing `requireCustomer`. If an invoice ever points to a customer that really doesn't exist, the export stops with a clear message like `error: Unknown customer "C-404" (referenced by invoice INV-9)` and exits with status 1, instead of crashing with a TypeError. It still never skips an invoice, as the README requires.
- **Tests**: one checks that CRM IDs are renamed on load (`tests/sources.test.js`), and one checks the error for an unknown customer (`tests/export.test.js`).

You can make the file for accounting with `npm run export > invoices.csv`. I haven't committed anything; tell me if you want me to.