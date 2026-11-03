import assert from "node:assert/strict";
import { test } from "node:test";
import { TtlCache } from "../src/cache.ts";

test("entries live for the default ttl", () => {
  const cache = new TtlCache<string>("5m");
  cache.set("a", "value", undefined, 1_000);
  assert.equal(cache.get("a", 1_000 + 299_999), "value");
  assert.equal(cache.get("a", 1_000 + 300_000), undefined);
});

test("a ttl given to set wins over the default", () => {
  const cache = new TtlCache<number>("5m");
  cache.set("a", 1, "10s", 0);
  assert.equal(cache.get("a", 9_999), 1);
  assert.equal(cache.get("a", 10_000), undefined);
});
