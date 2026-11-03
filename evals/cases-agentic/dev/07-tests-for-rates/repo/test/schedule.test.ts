import assert from "node:assert/strict";
import { test } from "node:test";
import { nextBusinessDay } from "../src/schedule.ts";

function day(iso: string): Date {
  return new Date(`${iso}T00:00:00Z`);
}

test("nextBusinessDay moves a weekday to the following day", () => {
  assert.deepEqual(nextBusinessDay(day("2026-03-03")), day("2026-03-04"));
});

test("nextBusinessDay skips the weekend", () => {
  assert.deepEqual(nextBusinessDay(day("2026-03-06")), day("2026-03-09"));
  assert.deepEqual(nextBusinessDay(day("2026-03-07")), day("2026-03-09"));
  assert.deepEqual(nextBusinessDay(day("2026-03-08")), day("2026-03-09"));
});

test("nextBusinessDay ignores the time of day and does not change its input", () => {
  const evening = new Date("2026-03-05T23:30:00Z");
  assert.deepEqual(nextBusinessDay(evening), day("2026-03-06"));
  assert.equal(evening.toISOString(), "2026-03-05T23:30:00.000Z");
});
