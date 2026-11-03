The bug comes from two calls on an empty array. `average([])` computes `0 / 0`, which is `NaN`, and `Math.max()` with no arguments returns `-Infinity`. I fixed it in `summarize` and left `average` alone, since it's exported and other callers may depend on its current behavior.

```js
// stats.js
function average(values) {
  let sum = 0;
  for (const v of values) sum += v;
  return sum / values.length;
}

function summarize(orders) {
  if (orders.length === 0) return emptySummary();

  const amounts = orders.map(o => o.amount);
  return {
    count: orders.length,
    avg: average(amounts).toFixed(2),
    max: Math.max(...amounts),
  };
}

function emptySummary() {
  return { count: 0, avg: "0.00", max: 0 };
}

module.exports = { average, summarize };
```

Add these tests to `stats.test.js` (I couldn't see the file, so I'm assuming it already imports from `./stats`):

```js
const { summarize } = require("./stats");

describe("summarize", () => {
  test("returns zeroed summary for a customer with no orders", () => {
    expect(summarize([])).toEqual({ count: 0, avg: "0.00", max: 0 });
  });

  test("summarizes existing orders", () => {
    const orders = [{ amount: 10 }, { amount: 20 }, { amount: 40 }];
    expect(summarize(orders)).toEqual({ count: 3, avg: "23.33", max: 40 });
  });
});
```

I haven't run these, so please run `npx jest stats.test.js` to confirm.

- **Empty-state values are my choice.** I used `"0.00"` and `0` so the dashboard keeps rendering numbers. If you'd rather show a placeholder like "—", return `avg: null, max: null` from `emptySummary()` instead. The UI would then need to handle `null`.
- **Guard clause:** the early return keeps the main path unchanged, and `emptySummary()` gives the empty case a name.
- **Possible follow-up:** `Math.max(...amounts)` can throw a `RangeError` for very large order lists (roughly 100k+ items). It's unrelated to this bug, so I left it.