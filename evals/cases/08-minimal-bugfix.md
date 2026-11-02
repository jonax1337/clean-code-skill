# Minimal bugfix with regression test (JavaScript)

Tests: fix the root cause, regression test, minimal diff, explicit decision on the edge case.

## Prompt

Bug report: the dashboard shows `NaN` and `-Infinity` for customers who have no orders yet. Please fix it. We use Jest; tests live in `stats.test.js`.

```js
// stats.js
function average(values) {
  let sum = 0;
  for (const v of values) sum += v;
  return sum / values.length;
}

function summarize(orders) {
  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: Math.max(...amounts),
  };
}

module.exports = { average, summarize };
```

## Assertions

1. Both symptoms are fixed: an empty order list yields neither `NaN` for `avg` nor `-Infinity` for `max`.
2. A Jest regression test for the empty case is added.
3. The fix is minimal: the output shape for non-empty input is unchanged and unrelated code is not rewritten.
4. The response states explicitly what the empty case now returns (e.g. `0`, `"0.00"` or `null`) and why.
5. No leftover debug output and no comments that narrate the fix.
