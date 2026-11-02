Customers with no orders produce an empty `amounts` array, and two calculations break on it:

- `average([])` computes `0 / 0`, which is `NaN`, so `toFixed(2)` gives `"NaN"`.
- `Math.max()` with no arguments returns `-Infinity`.

The fix is to handle the no-orders case explicitly in `summarize`.

```js
// stats.js
function average(values) {
  let sum = 0;
  for (const v of values) sum += v;
  return sum / values.length;
}

function summarize(orders) {
  if (orders.length === 0) return emptySummary();

  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: Math.max(...amounts),
  };
}

function emptySummary() {
  return { count: 0, avg: '0.00', max: 0 };
}

module.exports = { average, summarize };
```

Add these tests to `stats.test.js` (merge the import with your existing one if you already have it):

```js
const { summarize } = require('./stats');

describe('summarize', () => {
  it('returns zeroed values for a customer with no orders', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });

  it('summarizes existing orders as before', () => {
    const orders = [{ amount: 10 }, { amount: 20 }, { amount: 5 }];
    expect(summarize(orders)).toEqual({ count: 3, avg: '11.67', max: 20 });
  });
});
```

I haven't run these, so please run `npx jest stats.test.js` to confirm.

- **Placeholder values:** I used `0` and `'0.00'` as the empty-state values, since the dashboard's intended display wasn't specified. If you'd rather show "—" or "N/A", return `null` for `avg` and `max` instead and have the UI render the placeholder. Only `emptySummary` and the first test would change.
- **`average` unchanged:** I left `average` alone because it's exported and other callers may rely on its current behavior. It still returns `NaN` for an empty array, so any other caller passing an empty list would need the same guard.