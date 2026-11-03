Customers with no orders hit two empty-list edge cases in `summarize`:

- `average([])` computes `0 / 0`, which is `NaN`.
- `Math.max(...[])` returns `-Infinity`.

I couldn't run anything here, so the test and fix below are untested.

## 1. Failing test first

Add to `stats.test.js`:

```js
const { summarize } = require('./stats');

describe('summarize', () => {
  test('customer with no orders has no avg or max, not NaN/-Infinity', () => {
    expect(summarize([])).toEqual({ count: 0, avg: null, max: null });
  });

  test('customer with orders still gets formatted avg and max', () => {
    const result = summarize([{ amount: 10 }, { amount: 25 }]);
    expect(result).toEqual({ count: 2, avg: '17.50', max: 25 });
  });
});
```

The first test should currently fail with `avg: "NaN"` and `max: -Infinity`. The second test pins the existing behavior.

## 2. Smallest fix

In `stats.js`, only `summarize` changes:

```js
function summarize(orders) {
  if (orders.length === 0) return { count: 0, avg: null, max: null };

  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: Math.max(...amounts),
  };
}
```

The empty case is decided in one place, and `average` is unchanged. `avg` and `max` are `null` because "no orders" has no average or maximum, and `0` would claim a real value.

## Things to check

- **Dashboard rendering:** I chose `null` without seeing the UI code. If it prints values directly, it will show "null", so render it as `—` or `N/A`. If the product wants `"0.00"` and `0`, that is a one-line change in the early return and the first test.
- **`average([])`:** it still returns `NaN` if another caller passes an empty list. I left it alone to keep the edit small. If other callers exist, the same guard belongs there.

## Log

1. Diagnosed the `NaN` and `-Infinity` as `0/0` and `Math.max()` on an empty array.
2. Wrote a failing test for the empty case and a pinning test for the non-empty case, to prove behavior is unchanged.
3. Added a single early return in `summarize`.
4. Not done: I couldn't run Jest, so the "see it fail" step is unverified. The crapper, dryer and mutator tools aren't available in this session. There is no git repo, so I made no commits.