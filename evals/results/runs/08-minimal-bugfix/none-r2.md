Both symptoms come from empty `orders`: `average([])` computes `0 / 0`, which is `NaN`, and `Math.max()` with no arguments returns `-Infinity`.

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
  test('average of no values is 0', () => {
    expect(average([])).toBe(0);
  });

  test('summarize with no orders returns zeroed stats', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });
});

test('summarize with orders still works', () => {
  expect(summarize([{ amount: 10 }, { amount: 30 }]))
    .toEqual({ count: 2, avg: '20.00', max: 30 });
});
```

Two notes:

- **Default values:** I chose `0` / `'0.00'` for customers with no orders. If the dashboard should show "N/A" instead, return `null` for `avg` and `max` in that case and let the UI render the placeholder. That's often more accurate, since "no orders" isn't the same as "average of $0".
- **Large arrays:** `Math.max(...amounts)` can throw a `RangeError` with very large arrays (roughly 100k+ elements). If a customer could have that many orders, use `amounts.reduce((a, b) => Math.max(a, b), -Infinity)` instead, guarded for the empty case.

I haven't run the tests, since I can't execute anything in this session.