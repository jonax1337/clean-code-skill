The cause is empty input. With no orders, `average([])` computes `0 / 0`, which is `NaN`, and `Math.max(...[])` returns `-Infinity`.

```js
// stats.js
function average(values) {
  if (values.length === 0) return 0;
  let sum = 0;
  for (const v of values) sum += v;
  return sum / values.length;
}

function summarize(orders) {
  if (orders.length === 0) {
    return { count: 0, avg: (0).toFixed(2), max: 0 };
  }
  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: Math.max(...amounts),
  };
}

module.exports = { average, summarize };
```

Tests to add to `stats.test.js`:

```js
const { average, summarize } = require('./stats');

describe('empty input', () => {
  test('average of no values is 0, not NaN', () => {
    expect(average([])).toBe(0);
  });

  test('summarize with no orders returns zeroed stats', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });
});

test('summarize with orders still works', () => {
  expect(summarize([{ amount: 10 }, { amount: 20 }]))
    .toEqual({ count: 2, avg: '15.00', max: 20 });
});
```

I chose `0` / `"0.00"` as the "no orders" values so the dashboard shows a number. If you'd rather show a placeholder like "—" for these customers, return `null` for `avg` and `max` instead, and have the UI render it. I can switch it if you prefer that.

I haven't run the tests, since I can't execute anything in this session.