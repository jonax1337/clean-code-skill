Customers with no orders hit two separate bugs: `average([])` computes `0 / 0`, which is `NaN`, and `Math.max()` with no arguments returns `-Infinity`. Both are fixed below.

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
    max: amounts.length > 0 ? Math.max(...amounts) : 0,
  };
}

module.exports = { average, summarize };
```

I couldn't see `stats.test.js`, so append these tests there (skip the `require` if it's already imported):

```js
const { average, summarize } = require('./stats');

describe('customers with no orders', () => {
  test('average of no values is 0, not NaN', () => {
    expect(average([])).toBe(0);
  });

  test('summarize of no orders shows zeros, not NaN or -Infinity', () => {
    expect(summarize([])).toEqual({ count: 0, avg: '0.00', max: 0 });
  });
});

test('summarize still reports avg and max for existing orders', () => {
  expect(summarize([{ amount: 10 }, { amount: 20 }]))
    .toEqual({ count: 2, avg: '15.00', max: 20 });
});
```

- **Empty value:** I chose `0` / `"0.00"` because it keeps the types the dashboard already receives (`avg` is a string, `max` is a number) and matches `count: 0`. If the dashboard should show "no data" (for example `—`), return `null` for `avg` and `max` instead. That is a small change, but the dashboard would then need to handle `null`.
- **Not run:** I haven't run Jest or the tests, since I can't execute anything in this session. Please run `npx jest stats.test.js` before merging.
- **Out of scope:** `Math.max(...amounts)` can throw a `RangeError` for very large arrays (on the order of 100k+ orders). I left it alone, but it's worth a look if any customer has that many orders.