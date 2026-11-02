The cause is that an empty `orders` array makes `average([])` compute `0 / 0`, which is `NaN`, and `Math.max()` with no arguments returns `-Infinity`. The fix is to handle the empty case explicitly.

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
    return { count: 0, avg: "0.00", max: 0 };
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
const { average, summarize } = require("./stats");

describe("empty input", () => {
  test("average of an empty array is 0, not NaN", () => {
    expect(average([])).toBe(0);
  });

  test("summarize with no orders returns safe defaults", () => {
    expect(summarize([])).toEqual({ count: 0, avg: "0.00", max: 0 });
  });
});

test("summarize with orders still works", () => {
  expect(summarize([{ amount: 10 }, { amount: 20 }])).toEqual({
    count: 2,
    avg: "15.00",
    max: 20,
  });
});
```

- **Default values:** I chose `0` / `"0.00"` so the dashboard renders a sensible number. If you'd rather show "no data" (for example `—`), return `avg: null, max: null` instead and have the UI handle `null`. The tests would need to change to match.
- **Large arrays:** `Math.max(...amounts)` can throw a `RangeError` for very large arrays (on the order of 100k+ items). If customers can have that many orders, replace it with `amounts.reduce((m, a) => Math.max(m, a), -Infinity)` inside the non-empty branch.

I haven't run the tests, since I can't execute anything in this session.