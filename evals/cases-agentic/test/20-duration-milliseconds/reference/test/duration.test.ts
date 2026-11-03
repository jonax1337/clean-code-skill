import assert from "node:assert/strict";
import { test } from "node:test";
import { parseDuration } from "../src/duration.ts";

test("parses each unit", () => {
  assert.equal(parseDuration("30s"), 30_000);
  assert.equal(parseDuration("5m"), 300_000);
  assert.equal(parseDuration("2h"), 7_200_000);
  assert.equal(parseDuration("1d"), 86_400_000);
});

test("ignores surrounding whitespace", () => {
  assert.equal(parseDuration(" 10s "), 10_000);
});

test("rejects text that is not a duration", () => {
  assert.throws(() => parseDuration("soon"), /Invalid duration/);
  assert.throws(() => parseDuration("10"), /Invalid duration/);
  assert.throws(() => parseDuration("1.5h"), /Invalid duration/);
});
