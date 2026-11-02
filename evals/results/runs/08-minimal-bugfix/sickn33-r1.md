The cause is two empty-array edge cases. With no orders, `average([])` computes `0 / 0`, which is `NaN`, and `Math.max()` with no arguments returns `-Infinity`.

I chose `"0.00"` and `0` as the values for "no orders", because they keep the existing types (`avg` is a string, `max` is a number) and the dashboard won't need new handling. If you'd rather show a placeholder like "—", return `null` instead and have the UI handle it. I haven't run any of this, so please run the tests yourself.

```js
// stats.js
function average(values) {
  if (values.length === 0) return 0;
  return sum(values) / values.length;
}

function sum(values) {
  let total = 0;
  for (const v of values) total += v;
  return total;
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

Tests to add to `stats.test.js`. The two empty-case tests should fail against the old code and pass now:

```js
const { average, summarize } = require('./stats');

describe('average', () => {
  it('returns 0 for no values', () => {
    expect(average([])).toBe(0);
  });

  it('averages the values', () => {
    expect(average([2, 4, 9])).toBe(5);
  });
});

describe('summarize', () => {
  it('returns zeroed stats for a customer with no orders', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });

  it('summarizes existing orders', () => {
    const orders = [{ amount: 10 }, { amount: 20.5 }];
    expect(summarize(orders)).toEqual({ count: 2, avg: '15.25', max: 20.5 });
  });
});
```

Changes beyond the fix:
- I extracted `sum` and `maximum` so each function does one thing and `summarize` reads at a single level of abstraction.
- `Math.max(...amounts)` can throw a `RangeError` for very large arrays (on the order of 100k+ items). That's unrelated to this bug, so I left it, but it's worth watching if a customer could have that many orders.