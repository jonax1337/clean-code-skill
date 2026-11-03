Both symptoms come from `summarize` receiving an empty `orders` array:

- `average([])` computes `0 / 0`, which is `NaN`, and `NaN.toFixed(2)` gives the string `"NaN"`.
- `Math.max()` with no arguments returns `-Infinity`.

**Fix in `stats.js`:** return early when there are no orders.

```js
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

**Tests to add to `stats.test.js`:**

```js
const { summarize } = require('./stats');

describe('summarize', () => {
  test('returns count 0 and null avg/max for a customer with no orders', () => {
    expect(summarize([])).toEqual({ count: 0, avg: null, max: null });
  });

  test('returns count, formatted average and max for existing orders', () => {
    expect(summarize([{ amount: 10 }, { amount: 5 }]))
      .toEqual({ count: 2, avg: '7.50', max: 10 });
  });
});
```

The first test fails on the old code (it would get `"NaN"` and `-Infinity`). The second pins the existing behavior for non-empty input.

**Things to check:**

- **Design choice:** I return `null` for `avg` and `max` rather than `0` or `"0.00"`, because "no data" shouldn't look like a real average of zero. The dashboard must now render `null` as something like "–". If it expects a string or number there, tell me and I'll return `"0.00"` and `0` instead.
- **`average` is unchanged:** `average([])` still returns `NaN`. I guarded in `summarize` because I can't see the other callers of `average`, and changing its empty-input result could affect them.
- **Not run:** I can't execute anything in this session, so I haven't run Jest. Please run it on your side.
- **Left alone:** `Math.max(...amounts)` can throw a `RangeError` for very large order lists (spread argument limits). That's unrelated to this bug, so I didn't touch it.