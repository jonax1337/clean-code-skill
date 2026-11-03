import assert from "node:assert/strict";
import { test } from "node:test";
import { backoffDelayMs, withRetry } from "../src/retry.ts";

test("the backoff delay doubles with every attempt", () => {
  assert.equal(backoffDelayMs("2s", 0), 2000);
  assert.equal(backoffDelayMs("2s", 1), 4000);
  assert.equal(backoffDelayMs("1m", 2), 240000);
});

test("withRetry sleeps between failed attempts and returns the first success", async () => {
  const sleeps: number[] = [];
  let calls = 0;
  const result = await withRetry(
    async () => {
      calls++;
      if (calls < 3) {
        throw new Error("flaky");
      }
      return "done";
    },
    { attempts: 5, backoff: "1s" },
    async (ms) => {
      sleeps.push(ms);
    },
  );
  assert.equal(result, "done");
  assert.deepEqual(sleeps, [1000, 2000]);
});

test("withRetry rethrows the last error once the attempts are used up", async () => {
  await assert.rejects(
    withRetry(
      async () => {
        throw new Error("down");
      },
      { attempts: 2, backoff: "1s" },
      async () => {},
    ),
    /down/,
  );
});
