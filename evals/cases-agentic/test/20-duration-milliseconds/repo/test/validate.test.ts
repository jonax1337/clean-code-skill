import assert from "node:assert/strict";
import { test } from "node:test";
import { validateTtl } from "../src/validate.ts";

test("rejects text that is not a duration", () => {
  assert.match(validateTtl("soon") ?? "", /not a duration/);
});

test("rejects a ttl above the maximum", () => {
  assert.match(validateTtl("2d") ?? "", /exceeds/);
});
