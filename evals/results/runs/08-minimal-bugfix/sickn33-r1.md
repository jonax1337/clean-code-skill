The bug is in `summarize`. With no orders, `average([])` computes `0 / 0`, which is `NaN`, and `Math.max()` of nothing is `-Infinity`. I fixed it by handling the empty case explicitly at the top of `summarize`.

```js
// stats.js
function average(values) {
  let sum = 0;
  for (const v of values) sum += v;
  return sum / values.length;
}

function emptySummary() {
  return { count: 0, avg: (0).toFixed(2), max: 0 };
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

module.exports = { average, summarize };
```

Add these tests to `stats.test.js`. I couldn't see that file, so I'm assuming it already imports from `./stats`:

```js
const { summarize } = require('./stats');

describe('summarize', () => {
  it('returns zeroed values for a customer with no orders', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });

  it('still summarizes customers who have orders', () => {
    const orders = [{ amount: 10 }, { amount: 25 }];
    expect(summarize(orders)).toEqual({ count: 2, avg: '17.50', max: 25 });
  });
});
```

I haven't run these, so please run `npx jest stats.test.js` to confirm.

- **Zero vs. blank:** I chose `'0.00'` and `0` so the output keeps the same types the dashboard already receives (`avg` is a string, `max` is a number). If you'd rather show "—" or "N/A" for customers with no orders, return `null` for `avg` and `max` instead and have the dashboard render that. That is a product decision, so say if you want it.
- **`average` unchanged:** `average([])` still returns `NaN`. I left it alone so other callers don't change behavior. If nothing else uses it on empty input, you could make it return `0` as well.