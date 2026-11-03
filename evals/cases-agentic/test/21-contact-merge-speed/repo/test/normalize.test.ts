import assert from "node:assert/strict";
import { test } from "node:test";
import { normalizeEmail } from "../src/normalize.ts";

test("normalizeEmail trims and lower-cases", () => {
  assert.equal(normalizeEmail("  Ada@Example.COM "), "ada@example.com");
});
