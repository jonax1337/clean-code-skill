Both values come from empty `amounts`: `0 / 0` is `NaN`, and `Math.max()` with no arguments is `-Infinity`. The fix is to guard the empty case.

```js
// stats.js
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
    max: amounts.length ? Math.max(...amounts) : 0,
  };
}

module.exports = { average, summarize };
```

Tests to add to `stats.test.js`:

```js
const { average, summarize } = require('./stats');

describe('empty input', () => {
  test('average of an empty array is 0', () => {
    expect(average([])).toBe(0);
  });

  test('summarize with no orders returns zeros, not NaN/-Infinity', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });
});

describe('summarize with orders', () => {
  test('computes count, avg and max', () => {
    const result = summarize([{ amount: 10 }, { amount: 20 }, { amount: 30 }]);
    expect(result).toEqual({ count: 3, avg: '20.00', max: 30 });
  });
});
```

Notes:
- I chose `0` / `"0.00"` as the "no orders" values, since the dashboard expects a number and a formatted string. If you'd rather show a placeholder like "–", return `null` for `avg` and `max` in the empty case instead, and have the UI render that. That would be a small change in `summarize`.
- I also replaced `Math.max(...amounts)` only for the empty case. For very large order lists (roughly 100k+ items), spreading into `Math.max` can throw a `RangeError`. If customers can have that many orders, use `amounts.reduce((a, b) => Math.max(a, b), 0)` instead. Note that this assumes amounts are non-negative.

I haven't run the tests, since I can't execute anything in this session. Run `npx jest stats.test.js` to confirm.