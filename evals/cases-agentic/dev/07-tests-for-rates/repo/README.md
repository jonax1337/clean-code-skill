# payout-tools

Helpers for the payout service: amount formatting, IBAN checks, payout dates and currency conversion with fees.

All amounts are whole numbers of minor units (cents, yen, fils).

## Development

```sh
npm install
npm test            # node --test, runs test/*.test.ts
npm run typecheck   # tsc --noEmit
```

Tests live in `test/`, one `<module>.test.ts` per module in `src/`, written with `node:test` and `node:assert/strict`.
