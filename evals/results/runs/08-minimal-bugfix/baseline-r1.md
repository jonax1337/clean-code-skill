Both symptoms come from an empty `orders` array:

- `average([])` computes `0 / 0`, which is `NaN`, and `.toFixed(2)` turns that into the string `"NaN"`.
- `Math.max(...[])` returns `-Infinity`.

The fix is to handle the empty case explicitly.

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
  test('average of an empty array is 0', () => {
    expect(average([])).toBe(0);
  });

  test('summarize with no orders returns zeroed stats', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });
});

describe('non-empty input', () => {
  test('summarize computes count, avg and max', () => {
    const result = summarize([{ amount: 10 }, { amount: 20 }, { amount: 30 }]);
    expect(result).toEqual({ count: 3, avg: '20.00', max: 30 });
  });
});
```

**Decision for you:** I chose `0` / `"0.00"` as the "no orders" values so the dashboard formatting stays unchanged. If you'd rather show "no data" (for example `—`), return `avg: null, max: null` instead and have the dashboard render that. In that case, update the tests to expect `null`.

I haven't run the tests, since I can't execute anything in this session.