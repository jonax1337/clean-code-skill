The cause is that `summarize` runs on an empty `orders` array. `average([])` is `0 / 0`, which is `NaN`, and `Math.max()` with no arguments is `-Infinity`. I added an early return for the no-orders case.

```js
// stats.js
function summarize(orders) {
  if (orders.length === 0) {
    return { count: 0, avg: null, max: null };
  }

  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: Math.max(...amounts),
  };
}
```

Add these tests to `stats.test.js`. Skip the `require` line if `summarize` is already imported there.

```js
const { summarize } = require('./stats');

describe('summarize', () => {
  test('returns null avg and max for a customer with no orders', () => {
    expect(summarize([])).toEqual({ count: 0, avg: null, max: null });
  });

  test('summarizes a single order', () => {
    expect(summarize([{ amount: 12.5 }])).toEqual({ count: 1, avg: '12.50', max: 12.5 });
  });
});
```

- **Empty-case value:** I chose `null` so "no data" isn't shown as a real `0.00`. I can't see the dashboard code, so please check that it renders `null` as something sensible, such as "–". If you'd rather show `'0.00'` and `0`, it's a one-line change in the early return.
- **`average` unchanged:** it still returns `NaN` for an empty array. I fixed the problem in `summarize` to keep the exported function's behavior stable. If other callers pass empty arrays, they have the same issue.
- **Not run:** I couldn't run Jest here, and I haven't seen your existing tests. Please run `npx jest` to confirm.
- **Possible follow-up:** `Math.max(...amounts)` can throw a `RangeError` for very large order lists (roughly 100k+ items, depending on the engine). I left it alone since it's outside this bug.