The cause is two empty-array edge cases in `summarize` when `orders` is `[]`:

- `average([])` computes `0 / 0`, which is `NaN`, and `NaN.toFixed(2)` gives `"NaN"`.
- `Math.max()` with no arguments returns `-Infinity`.

I made the empty case explicit in both places, with a small `maximum` helper so `summarize` stays at one level of abstraction.

```js
// stats.js
function average(values) {
  if (values.length === 0) return 0;

  let sum = 0;
  for (const v of values) sum += v;
  return sum / values.length;
}

function maximum(values) {
  if (values.length === 0) return 0;

  return Math.max(...values);
}

function summarize(orders) {
  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: maximum(amounts),
  };
}

module.exports = { average, summarize };
```

Tests to add to `stats.test.js`, written to fail against the old code:

```js
describe('customers with no orders', () => {
  test('average of no values is 0', () => {
    expect(average([])).toBe(0);
  });

  test('summarize returns zeroed stats instead of NaN or -Infinity', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });
});

describe('customers with orders', () => {
  test('summarize is unchanged for non-empty orders', () => {
    const orders = [{ amount: 10 }, { amount: 25 }];
    expect(summarize(orders)).toEqual({ count: 2, avg: '17.50', max: 25 });
  });
});
```

You'll need `const { average, summarize } = require('./stats');` at the top if it isn't already there.

- **Product decision:** I chose `0` / `"0.00"` for the empty case because it keeps the types the same (`avg` stays a string, `max` stays a number). If the dashboard should show "—" or "N/A" for no data, return `null` from `maximum` and `average` instead and let the UI handle it. That's a one-line change in each helper, plus the test expectations.
- **Not run:** I can't execute anything in this session, so I haven't run the tests. Please run `npx jest stats.test.js` to confirm.
- **Out of scope:** `Math.max(...amounts)` can throw a `RangeError` for very large arrays (roughly 100k+ elements). I left it alone, but it's worth replacing with a `reduce` if customers can have that many orders.