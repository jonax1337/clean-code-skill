## Root cause

For a customer with no orders, `amounts` is `[]`:
- `average([])` computes `0 / 0`, which is `NaN`.
- `Math.max(...[])` is `-Infinity`, because that is the identity value for max.

Neither function handles the empty case, so both leak a math artifact into the UI.

## 1. Failing tests first (`stats.test.js`)

Add these to the existing file:

```js
const { average, summarize } = require('./stats');

describe('empty input', () => {
  test('average of no values is 0, not NaN', () => {
    expect(average([])).toBe(0);
  });

  test('summarize of no orders shows zeros, not NaN or -Infinity', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });
});

describe('non-empty input (behavior pinned)', () => {
  test('summarize reports count, avg and max', () => {
    const orders = [{ amount: 10 }, { amount: 20 }, { amount: 40 }];
    expect(summarize(orders)).toEqual({ count: 3, avg: '23.33', max: 40 });
  });
});
```

Expected failures before the fix:
- `average([])` gives `NaN`, not `0`.
- `summarize([])` gives `avg: 'NaN'` and `max: -Infinity`.

The non-empty test should already pass. It pins the existing behavior.

## 2. Smallest fix (`stats.js`)

```js
function average(values) {
  if (values.length === 0) return 0;
  let sum = 0;
  for (const v of values) sum += v;
  return sum / values.length;
}

function summarize(orders) {
  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: amounts.length === 0 ? 0 : Math.max(...amounts),
  };
}

module.exports = { average, summarize };
```

## Notes

- **Product decision:** I chose `0` / `"0.00"` for "no orders" because it's the least disruptive for a dashboard. If you'd rather show "—" or "N/A", return `null` in both places instead and have the UI render it. That's a two-line change, and the tests above would change to match.
- **Not run:** I can't execute Jest in this session, so the red-then-green sequence above is what I expect, not something I observed. Please run `npx jest stats.test.js` to confirm.
- **Out of scope:** `Math.max(...amounts)` can throw a `RangeError` for very large order lists (roughly 100k+ items). I left it alone, but a `reduce` would avoid it if customers can have that many orders.
- **Not done:** this folder isn't a git repo, so I made no commit. I also didn't run the crapper, dryer, or mutator tools, since they aren't available here. Both functions are tiny and low-complexity.

## Log

1. Reasoned about the root cause: `0/0` and `Math.max()` on an empty array.
2. Wrote failing tests for the empty cases and a pinning test for the non-empty case, before touching the code.
3. Fixed `average` at the source, so every caller benefits, and guarded `max` in `summarize`.
4. Flagged the display-value decision, the untested run, and the spread-size risk.