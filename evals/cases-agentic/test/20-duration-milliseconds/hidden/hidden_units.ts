import assert from "node:assert/strict";
import { test } from "node:test";
import { describeSettings, rateLimitHeaders, validateTtl } from "../src/index.ts";

test("validateTtl accepts every ttl between 5 seconds and one day", () => {
  assert.equal(validateTtl("5s"), null);
  assert.equal(validateTtl("2h"), null);
  assert.equal(validateTtl("1d"), null);
});

test("validateTtl rejects a ttl outside the allowed range", () => {
  assert.match(validateTtl("4s") ?? "", /minimum/);
  assert.match(validateTtl("0s") ?? "", /minimum/);
  assert.match(validateTtl("25h") ?? "", /maximum/);
  assert.match(validateTtl("soon") ?? "", /not a duration/);
});

test("Retry-After is still sent in whole seconds", () => {
  assert.deepEqual(rateLimitHeaders("90s"), { "Retry-After": "90" });
  assert.deepEqual(rateLimitHeaders("2m"), { "Retry-After": "120" });
});

test("the settings report still prints seconds", () => {
  assert.equal(describeSettings({ timeout: "30s", ttl: "5m" }), "timeout 30s, ttl 300s");
});
