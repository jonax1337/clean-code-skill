The export works now. `npm run export` exits 0 and writes all 8 invoices, INV-1038 to INV-1045, and INV-1041 shows up as `Birch & Co, 120.00`. All 13 tests pass, including two new ones.

**Cause:** the two customer files name the ID field differently. `billing-customers.json` uses `customerId`, but `crm-customers.json` uses `customer_id`. Because of that, the export couldn't find any customer created in the CRM (C-2201, C-2202, C-2203), so invoices INV-1041, INV-1043 and INV-1045 crashed it.

**Changes:**
- `src/sources.js`: CRM records are now converted to `customerId` when the file is loaded. I didn't edit the data files, since the README says they're read exactly as delivered.
- `src/export.js`: the customer lookup now goes through `requireCustomer`, as the README requires. If an invoice ever points to a customer that really doesn't exist, the export stops with a clear error like `Unknown customer "C-9" (referenced by invoice INV-9)` and exit code 1. It no longer crashes with the confusing TypeError, and it still doesn't write a partial file.
- `tests/export.test.js`: added tests for CRM customers and for the unknown-customer error.

The CSV columns haven't changed, so accounting's import will still work. I haven't committed anything; tell me if you want me to.