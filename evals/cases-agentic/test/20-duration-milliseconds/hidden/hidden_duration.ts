import assert from "node:assert/strict";
import { test } from "node:test";
import { parseDuration } from "../src/index.ts";

test("parseDuration returns milliseconds for every unit", () => {
  assert.equal(parseDuration("30s"), 30_000);
  assert.equal(parseDuration("5m"), 300_000);
  assert.equal(parseDuration("2h"), 7_200_000);
  assert.equal(parseDuration("1d"), 86_400_000);
  assert.equal(parseDuration("0s"), 0);
});

test("parseDuration still trims whitespace and rejects invalid text", () => {
  assert.equal(parseDuration(" 10s "), 10_000);
  assert.throws(() => parseDuration("soon"), /Invalid duration/);
  assert.throws(() => parseDuration("1.5h"), /Invalid duration/);
});
