# sales-reports

Turns a list of regional sales into the monthly text report that finance imports, and into the weekly digest
lines for the sales channel.

- `src/report.js` builds the report (`buildReport`) and formats amounts (`formatMoney`).
- `src/export.js` wraps the report in the finance export format.
- `src/digest.js` lists the biggest deals of a period.
- `src/sales.js` parses the JSON dump from the order system.
- `src/cli.js` prints the finance export for a JSON file: `node src/cli.js data/sample.json 2024-03`.

## Tests

Plain Node, no dependencies:

```
npm test
```

(`npm test` runs `node --test`.)
