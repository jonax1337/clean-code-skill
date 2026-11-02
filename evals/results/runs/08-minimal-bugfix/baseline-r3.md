The cause is two empty-array edge cases. With no orders, `average([])` computes `0 / 0`, which is `NaN`, and `Math.max(...[])` returns `-Infinity`.

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

Add these tests to `stats.test.js`:

```js
const { average, summarize } = require('./stats');

describe('empty input', () => {
  test('average of an empty array is 0, not NaN', () => {
    expect(average([])).toBe(0);
  });

  test('summarize with no orders returns zeros', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });
});

describe('non-empty input', () => {
  test('summarize computes count, avg and max', () => {
    const result = summarize([{ amount: 10 }, { amount: 20 }, { amount: 5 }]);
    expect(result).toEqual({ count: 3, avg: '11.67', max: 20 });
  });
});
```

I chose `0` / `"0.00"` as the "no orders" values so the dashboard displays something sensible. If you'd rather show a placeholder like "—", return `null` for `avg` and `max` in the empty branch and have the UI render that. Either way, the empty case is now handled explicitly. The `Math.max(...amounts)` spread can also hit argument limits on very large arrays (roughly 100k+ items). If customers can have that many orders, `amounts.reduce((m, a) => Math.max(m, a), -Infinity)` is safer.