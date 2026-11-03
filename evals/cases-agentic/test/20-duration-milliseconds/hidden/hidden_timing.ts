import assert from "node:assert/strict";
import { test } from "node:test";
import { TtlCache, backoffDelayMs, dueJobs, nextRun, withRetry } from "../src/index.ts";

test("backoffDelayMs keeps returning milliseconds", () => {
  assert.equal(backoffDelayMs("3s", 0), 3_000);
  assert.equal(backoffDelayMs("3s", 3), 24_000);
  assert.equal(backoffDelayMs("2m", 1), 240_000);
});

test("withRetry sleeps for the same number of milliseconds as before", async () => {
  const sleeps: number[] = [];
  await assert.rejects(
    withRetry(
      async () => {
        throw new Error("down");
      },
      { attempts: 4, backoff: "500s" },
      async (ms) => {
        sleeps.push(ms);
      },
    ),
  );
  assert.deepEqual(sleeps, [500_000, 1_000_000, 2_000_000]);
});

test("cache entries expire after the same wall-clock time as before", () => {
  const cache = new TtlCache<string>("1h");
  cache.set("a", "x", undefined, 10);
  cache.set("b", "y", "90s", 10);
  assert.equal(cache.get("a", 10 + 3_599_999), "x");
  assert.equal(cache.get("a", 10 + 3_600_000), undefined);
  assert.equal(cache.get("b", 10 + 89_999), "y");
  assert.equal(cache.get("b", 10 + 90_000), undefined);
});

test("scheduler computes timestamps in milliseconds", () => {
  const job = { name: "report", every: "1d", lastRun: 5_000 };
  assert.equal(nextRun(job), 5_000 + 86_400_000);
  assert.deepEqual(dueJobs([job], 5_000 + 86_399_999), []);
  assert.deepEqual(dueJobs([job], 5_000 + 86_400_000), [job]);
});
