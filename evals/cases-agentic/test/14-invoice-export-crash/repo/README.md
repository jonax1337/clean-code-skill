# invoice-export

Turns the invoices of the billing system into the CSV file the accounting team imports every month.

## Usage

```
npm run export > invoices.csv
```

This runs `node src/cli.js data`: it reads `invoices.json`, `billing-customers.json` and `crm-customers.json` from
the given directory (default `data/`) and prints one CSV row per invoice, in the order of `invoices.json`.

The customers come from two systems. `billing-customers.json` is exported by the billing system, and
`crm-customers.json` holds the customers that were created in the CRM. Both are read as they are delivered. The
accounting import expects the CSV columns `invoice_id,customer,issued_on,total`, so the format must not change.

## Tests

```
npm test
```

Plain `node --test`, no dependencies. Tests live in `tests/`.

## Conventions

- Money is handled in integer cents and formatted only at the edge (`src/money.js`).
- A reference to something that does not exist, such as an unknown customer, is a data error. It is reported with
  `UnknownReferenceError` naming what was not found (see `requireCustomer`), and the CLI then exits with status 1
  and prints nothing to stdout. The export never skips a record or prints a placeholder for it: a file with a
  missing invoice is worse for accounting than no file.
