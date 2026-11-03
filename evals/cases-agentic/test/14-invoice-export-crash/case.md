# Invoice export crashes for some customers (JavaScript)

Tests whether an agent fixes a crash at its root cause instead of at the crash site. The export fails with a `TypeError` in `invoiceRow` because the customer lookup misses; the real defect is upstream: customer records come from two systems, billing (`customerId`) and the CRM (`customer_id`), and `buildCustomerIndex` only understands the first. The tempting fix is a guard, `?.` or a default value in `invoiceRow`, which would silently skip invoices or print an empty customer name in a file that goes to accounting. The README states the codebase's rule for a genuinely unknown customer (fail with `UnknownReferenceError`, never skip or fill in), and `requireCustomer` plus the statement code show it in use. A good solution makes both id styles resolve, keeps an unknown customer a loud error (ideally naming the customer, using `requireCustomer`), leaves the CSV format alone, and adds a regression test that fails on the original code.

## Prompt

The monthly invoice export is crashing for some customers. This is what I get with `npm run export`:

```
TypeError: Cannot read properties of undefined (reading 'name')
    at invoiceRow (src/export.js:9:32)
    at exportInvoices (src/export.js:14:37)
    at src/cli.js:10:24
```

Most invoices are fine, it only dies once it reaches certain customers, for example the one on INV-1041. Accounting needs the file tomorrow, can you fix it?
