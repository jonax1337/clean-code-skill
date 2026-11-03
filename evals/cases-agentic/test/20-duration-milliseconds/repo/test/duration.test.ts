import assert from "node:assert/strict";
import { test } from "node:test";
import { parseDuration } from "../src/duration.ts";

test("parses each unit", () => {
  assert.equal(parseDuration("30s"), 30);
  assert.equal(parseDuration("5m"), 300);
  assert.equal(parseDuration("2h"), 7200);
  assert.equal(parseDuration("1d"), 86400);
});

test("ignores surrounding whitespace", () => {
  assert.equal(parseDuration(" 10s "), 10);
});

test("rejects text that is not a duration", () => {
  assert.throws(() => parseDuration("soon"), /Invalid duration/);
  assert.throws(() => parseDuration("10"), /Invalid duration/);
  assert.throws(() => parseDuration("1.5h"), /Invalid duration/);
});
