The cause is in `summarize` when `orders` is empty:

- `average([])` computes `0 / 0`, which is `NaN`, and `NaN.toFixed(2)` returns the string `"NaN"`.
- `Math.max(...[])` returns `-Infinity`.

The fix is to handle the no-orders case explicitly at the top of `summarize`, so the main path stays unchanged.

```js
// stats.js
function average(values) {
  let sum = 0;
  for (const v of values) sum += v;
  return sum / values.length;
}

function summarize(orders) {
  if (orders.length === 0) return summaryForNoOrders();

  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: Math.max(...amounts),
  };
}

function summaryForNoOrders() {
  return { count: 0, avg: (0).toFixed(2), max: 0 };
}

module.exports = { average, summarize };
```

I couldn't see `stats.test.js`, so here are tests to add to it. Write them first and confirm they fail against the old code (they will, with `"NaN"` and `-Infinity`):

```js
// stats.test.js
const { summarize } = require('./stats');

describe('summarize', () => {
  it('returns zeroed values for a customer with no orders', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });

  it('still summarizes customers who have orders', () => {
    const orders = [{ amount: 10 }, { amount: 30 }];
    expect(summarize(orders)).toEqual({ count: 2, avg: '20.00', max: 30 });
  });
});
```

I haven't run these, so please run `npx jest stats.test.js` to confirm.

Two things to check:

- **Product decision:** I chose `avg: "0.00"` and `max: 0` because they keep the existing types (string and number). If the dashboard should show "—" or "N/A" for new customers, return `null` for `avg` and `max` instead and have the UI render the placeholder. That's arguably more accurate, since a customer with no orders has no average, but it needs a matching UI change.
- **`average` is unchanged:** `average([])` still returns `NaN`. I left it alone to keep the fix in scope. If other callers use it with possibly empty arrays, it deserves the same guard or an explicit error.