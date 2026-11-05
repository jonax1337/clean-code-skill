`npm run export` now runs to the end and prints all eight invoices, including INV-1041 (Birch & Co). The existing 11 tests pass. I didn't add a test for the CRM case, and I haven't committed anything.

**Cause:** the customers come from two files that name the id field differently. `billing-customers.json` uses `customerId`, but `crm-customers.json` uses `customer_id`. The CRM customers (C-2201, C-2202, C-2203) were therefore indexed under `undefined`, and any invoice for one of them crashed the export. INV-1041, INV-1043 and INV-1045 were all affected.

**Changes:**
- **`src/sources.js`:** CRM records are converted from `customer_id` to `customerId` when loaded. The CSV format is unchanged.
- **`src/export.js`:** the export now looks customers up with `requireCustomer`. If an invoice points at a customer that really doesn't exist, you get the `UnknownReferenceError` message and exit status 1, as the README describes, instead of a `TypeError`.

Both data files are read as delivered, so nothing in `data/` was edited.