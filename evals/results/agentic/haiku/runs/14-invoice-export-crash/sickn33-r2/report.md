The export runs again. INV-1041 (and the other CRM customers) now appear with the right names, and all 14 tests pass.

**Cause:** `data/crm-customers.json` names the id field `customer_id`, while the rest of the code uses `customerId`. The customer index therefore stored Birch & Co, Lindqvist AB and Tulpen BV under `undefined`. The lookup for INV-1041 returned nothing, and `customer.name` threw. Billing customers were fine, which is why only some invoices failed.

**Changes:**
- `src/sources.js`: CRM records are mapped from `customer_id` to `customerId` when loaded. I left the delivered JSON files as they are, since the README says they are read as delivered.
- `src/export.js`: the lookup now goes through `requireCustomer`. A genuinely unknown customer gives `Unknown customer "C-…" (referenced by invoice INV-…)` and exit code 1, as the README describes, instead of a `TypeError` stack trace.
- Tests: new `tests/sources.test.js` covers the id mapping, and `tests/export.test.js` covers the unknown-customer error.

**Output check:** the totals match the invoice lines. INV-1041 is 8 × 15.00 = 120.00, and INV-1043 is 20 × 14.00 = 280.00.

The changes are uncommitted in the working tree. I haven't committed or pushed anything. Let me know if you want a commit.