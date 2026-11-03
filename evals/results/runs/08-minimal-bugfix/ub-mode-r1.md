Customers with no orders produce `NaN` and `-Infinity` because `average([])` computes `0 / 0` and `Math.max()` with no arguments returns `-Infinity`. I couldn't run anything in this session, so none of this has been executed.

## 1. Failing test first (`stats.test.js`)

Add this to the existing file:

```js
const { summarize } = require('./stats');

describe('summarize with no orders', () => {
  test('reports no average or max instead of NaN / -Infinity', () => {
    expect(summarize([])).toEqual({ count: 0, avg: null, max: null });
  });
});
```

It should currently fail with `avg: "NaN"` and `max: -Infinity`.

## 2. Smallest fix (`stats.js`)

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

The empty case is decided in one place, `summarize`, which is the only caller that turns `average` and `max` into dashboard values. `average` is unchanged.

## Decision for you
I chose `null` for "no data" because `0` or `"0.00"` would look like real spending. The dashboard must render `null` as something like "—". If you'd rather show `"0.00"` and `0`, change the two values in the early return and in the test.

## Log
- Traced `NaN` to `0 / 0` in `average([])` and `-Infinity` to `Math.max()` with no arguments, both reached only through `summarize([])`.
- Wrote the failing test for the empty case, to be run before the fix.
- Added a single early return in `summarize`, so one decision lives in one place.
- Not done, because I had no tools: running Jest, the crapper, dryer and mutator checks, and committing and pushing. Please run `npx jest` to confirm the test fails before the fix and passes after.